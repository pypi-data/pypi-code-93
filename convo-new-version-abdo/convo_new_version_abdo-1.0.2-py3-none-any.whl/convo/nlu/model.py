import copy
import datetime
import logging
import os
from typing import Any, Dict, List, Optional, Text

import convo.nlu
from convo.shared.exceptions import ConvoExceptions 
import convo.shared.utils.io
import convo.utils.io
from convo.constants import MIN_COMPATIBLE_VER, NLU_MODEL_AFFIX_NAME
from convo.nlu import components, utils  # pytype: disable=pyi-error
from convo.nlu.classifiers.classifier import (  # pytype: disable=pyi-error
    IntentionClassifier,
)
from convo.nlu.components import Element, ElementBuilder  # pytype: disable=pyi-error
from convo.nlu.config import ConvoNLUModelConfiguration, comp_configuration_from_pipeline
from convo.nlu.extractors.extractor import ExtractorEntity  # pytype: disable=pyi-error

from convo.nlu.persistor import Persevere
from convo.shared.nlu.constants import (
    TXT,
    ENTITIES_NAME,
    INTENTION,
    KEY_INTENT_NAME,
    KEY_PREDICTED_CONFIDENCE,
)
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.utils import write_json_to_file

log = logging.getLogger(__name__)


class NotvalidModelError(ConvoExceptions ):
    """Raised when a model failed to load.

    Attributes:
        message -- explanation of why the model is invalid
    """

    def __init__(self, message: Text) -> None:
        self.message = message
        super(NotvalidModelError, self).__init__()

    def __str__(self) -> Text:
        return self.message


class NotsupportedModelError(ConvoExceptions ):
    """Raised when a model is too old to be loaded.

    Attributes:
        message -- explanation of why the model is invalid
    """

    def __init__(self, message: Text) -> None:
        self.message = message
        super(NotsupportedModelError, self).__init__()

    def __str__(self) -> Text:
        return self.message


class Metadataset:
    """Captures all information about a model to load and prepare it."""

    @staticmethod
    def load(model_dir: Text):
        """Loads the metadata from a models dir.

        Args:
            model_dir: the dir where the model is saved.
        Returns:
            Metadataset: A metadata object describing the model
        """
        try:
            meta_data_file = os.path.join(model_dir, "metadata.json")
            data_set = convo.shared.utils.io.reading_json_file(meta_data_file)
            return Metadataset(data_set, model_dir)
        except Exception as e:
            absolute_path = os.path.abspath(os.path.join(model_dir, "metadata.json"))
            raise NotvalidModelError(
                f"Failed to load model metadata from '{absolute_path}'. {e}"
            )

    def __init__(self, metadata: Dict[Text, Any], model_dir: Optional[Text]):

        self.metadata = metadata
        self.model_dir = model_dir

    def get(self, property_name: Text, default: Any = None) -> Any:
        return self.metadata.get(property_name, default)

    @property
    def comp_classes(self):
        if self.get("pipeline"):
            return [c.get("class") for c in self.get("pipeline", [])]
        else:
            return []

    @property
    def no_of_comps(self):
        return len(self.get("pipeline", []))

    def for_comp(self, index: int, defaults: Any = None) -> Dict[Text, Any]:
        return comp_configuration_from_pipeline(index, self.get("pipeline", []), defaults)

    @property
    def lang(self) -> Optional[Text]:
        """Language of the underlying model"""

        return self.get("language")

    def persist(self, model_dir: Text):
        """Persists the metadata of a model to a given dir."""

        meta_data = self.metadata.copy()

        meta_data.update(
            {
                "trained_at": datetime.datetime.now().strftime("%Y%m%d-%H%M%S"),
                "convo_version": convo.__version__,
            }
        )

        file_name = os.path.join(model_dir, "metadata.json")
        write_json_to_file(file_name, meta_data, indent=4)


class Instructor:
    """Instructor will load the data and train all components.

    Requires a pipeline specification and configuration to use for
    the training.
    """

    def __init__(
        self,
        cfg: ConvoNLUModelConfiguration,
        comp_builder: Optional[ElementBuilder] = None,
        skip_validation: bool = False,
    ):

        self.config = cfg
        self.skip_validation = skip_validation
        self.training_data = None  # type: Optional[TrainingDataSet]

        if comp_builder is None:
            # If no builder is passed, every interpreter creation will result in
            # a new builder. hence, no components are reused.
            comp_builder = components.ElementBuilder()

        # Before instantiating the component classes, lets check if all
        # required packages are available
        if not self.skip_validation:
            components.requirements_validation(cfg.comp_names)

        # build pipeline
        self.pipeline = self.pipeline_building(cfg, comp_builder)

    def pipeline_building(
        self, cfg: ConvoNLUModelConfiguration, component_builder: ElementBuilder
    ) -> List[Element]:
        """Transform the passed names of the pipeline components into classes."""

        pipe_line = []

        # Transform the passed names of the pipeline components into classes
        for i in range(len(cfg.pipeline)):
            comp_configuration = cfg.for_comp(i)
            comp = component_builder.comp_creation(comp_configuration, cfg)
            pipe_line.append(comp)

        if not self.skip_validation:
            components.pipeline_validation(pipe_line)

        return pipe_line

    def train(self, data: TrainingDataSet, **kwargs: Any) -> "Interpreter":
        """Trains the underlying pipeline using the provided training data."""

        self.training_data = data

        self.training_data.validating()

        context_data = kwargs

        for component in self.pipeline:
            upgrade = component.give_context()
            if upgrade:
                context_data.update(upgrade)

        # Before the training starts: check that all arguments are provided
        if not self.skip_validation:
            components.required_comps_from_data_validation(
                self.pipeline, self.training_data
            )

        # data gets modified internally during the training - hence the copy
        working_data: TrainingDataSet = copy.deepcopy(data)

        for i, component in enumerate(self.pipeline):
            log.info(f"Starting to train component {component.name}")
            component.partial_processing_preparation(self.pipeline[:i], context_data)
            upgrade = component.train(working_data, self.config, **context_data)
            log.info("Finished training component.")
            if upgrade:
                context_data.update(upgrade)

        return Interpreter(self.pipeline, context_data)

    @staticmethod
    def filename(index: int, name: Text) -> Text:
        return f"component_{index}_{name}"

    def persist(
        self,
        path_flow: Text,
        persistor: Optional[Persevere] = None,
        fixed_model_name: Text = None,
        persist_nlu_training_data: bool = False,
    ) -> Text:
        """Persist all components of the pipeline to the passed path.

        Returns the dir of the persisted model."""

        time_stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        meta_data = {"language": self.config["language"], "pipeline": []}

        if fixed_model_name:
            name_of_model = fixed_model_name
        else:
            name_of_model = NLU_MODEL_AFFIX_NAME + time_stamp

        path_flow = os.path.abspath(path_flow)
        directory_name = os.path.join(path_flow, name_of_model)

        convo.shared.utils.io.create_dir(directory_name)

        if self.training_data and persist_nlu_training_data:
            meta_data.update(self.training_data.persist(directory_name))

        for i, component in enumerate(self.pipeline):
            name_of_file = self.filename(i, component.name)
            update = component.persist(name_of_file, directory_name)
            comp_meta_data = component.component_config
            if update:
                comp_meta_data.update(update)
            comp_meta_data["class"] = utils.module_path_from_object(component)

            meta_data["pipeline"].append(comp_meta_data)

        Metadataset(meta_data, directory_name).persist(directory_name)

        if persistor is not None:
            persistor.persist(directory_name, name_of_model)
        log.info(
            "Successfully saved model into '{}'".format(os.path.abspath(directory_name))
        )
        return directory_name


class Interpreter:
    """Use a trained pipeline of components to parse text messages."""

    # Defines all attributes (& default values)
    # that will be returned by `parse`
    @staticmethod
    def dfault_output_attrs() -> Dict[Text, Any]:
        return {
            TXT: "",
            INTENTION: {KEY_INTENT_NAME: None, KEY_PREDICTED_CONFIDENCE: 0.0},
            ENTITIES_NAME: [],
        }

    @staticmethod
    def verify_model_compatibility(
        metadata: Metadataset, version_checking: Optional[Text] = None
    ) -> None:
        from packaging import version

        if version_checking is None:
            version_checking = MIN_COMPATIBLE_VER

        model_ver = metadata.get("convo_version", "0.0.0")
        if version.parse(model_ver) < version.parse(version_checking):
            raise NotsupportedModelError(
                "The model version is too old to be "
                "loaded by this Convo NLU instance. "
                "Either retrain the model, or run with "
                "an older version. "
                "Model version: {} Instance version: {}"
                "".format(model_ver, convo.__version__)
            )

    @staticmethod
    def load(
        model_dir: Text,
        component_builder: Optional[ElementBuilder] = None,
        skip_validation: bool = False,
    ) -> "Interpreter":
        """Create an interpreter based on a persisted model.

        Args:
            skip_validation: If set to `True`, does not check that all
                required packages for the components are installed
                before loading them.
            model_dir: The path of the model to load
            component_builder: The
                :class:`convo.nlu.components.ElementBuilder` to use.

        Returns:
            An interpreter that uses the loaded model.
        """

        model_meta_data = Metadataset.load(model_dir)

        Interpreter.verify_model_compatibility(model_meta_data)
        return Interpreter.create(model_meta_data, component_builder, skip_validation)

    @staticmethod
    def create(
        model_metadata: Metadataset,
        component_builder: Optional[ElementBuilder] = None,
        skip_validation: bool = False,
    ) -> "Interpreter":
        """Load stored model and components defined by the provided metadata."""

        context_data = {}

        if component_builder is None:
            # If no builder is passed, every interpreter creation will result
            # in a new builder. hence, no components are reused.
            component_builder = components.ElementBuilder()

        pipe_line = []

        # Before instantiating the component classes,
        # lets check if all required packages are available
        if not skip_validation:
            components.requirements_validation(model_metadata.comp_classes)

        for i in range(model_metadata.no_of_comps):
            component_meta = model_metadata.for_comp(i)
            comp = component_builder.comp_loading(
                component_meta, model_metadata.model_dir, model_metadata, **context_data
            )
            try:
                upgrades = comp.give_context()
                if upgrades:
                    context_data.update(upgrades)
                pipe_line.append(comp)
            except components.AbsentArgumentError as e:
                raise Exception(
                    "Failed to initialize component '{}'. "
                    "{}".format(comp.name, e)
                )

        return Interpreter(pipe_line, context_data, model_metadata)

    def __init__(
        self,
        pipeline: List[Element],
        context: Optional[Dict[Text, Any]],
        model_metadata: Optional[Metadataset] = None,
    ) -> None:

        self.pipeline = pipeline
        self.context = context if context is not None else {}
        self.model_metadata = model_metadata

    def parse_func(
        self,
        text: Text,
        time: Optional[datetime.datetime] = None,
        only_output_properties: bool = True,
    ) -> Dict[Text, Any]:
        """Parse the input text, classify it and return pipeline result.

        The pipeline result usually contains intent and entities."""

        if not text:
            # Not all components are able to handle empty strings. So we need
            # to prevent that... This default return will not contain all
            # output attributes of all components, but in the end, no one
            # should pass an empty string in the first place.
            outp = self.dfault_output_attrs()
            outp["text"] = ""
            return outp

        data_set = self.dfault_output_attrs()
        data_set[TXT] = text

        msg = Msg(data=data_set, time=time)

        for component in self.pipeline:
            component.process(msg, **self.context)

        outp = self.dfault_output_attrs()
        outp.update(msg.as_dictionary(only_output_properties=only_output_properties))
        return outp

    def featurize_msg(self, message: Msg) -> Msg:
        """
        Tokenize and featurize the input message
        Args:
            message: message storing text to process;
        Returns:
            message: it contains the tokens and features which are the output of the NLU pipeline;
        """

        for component in self.pipeline:
            if not isinstance(component, (ExtractorEntity, IntentionClassifier)):
                component.process(message, **self.context)
        return message
