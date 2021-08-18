from collections import defaultdict
import itertools
import logging
import typing
from typing import Any, Dict, Hashable, List, Optional, Set, Text, Tuple, Type, Iterable

from convo.exceptions import DependencyExceptionMissing
from convo.shared.exceptions import ConvoExceptions 
from convo.shared.nlu.constants import EXTRACTORS_TRAINABLE
from convo.nlu.config import ConvoNLUModelConfiguration, overriding_dfault_values, InvalidConfigurationError
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
import convo.shared.utils.io

if typing.TYPE_CHECKING:
    from convo.nlu.model import Metadataset

log = logging.getLogger(__name__)


def search_not_available_packages(package_names: List[Text]) -> Set[Text]:
    """Tries to import all package names and returns the packages where it failed.

    Args:
        package_names: The package names to import.

    Returns:
        Package names that could not be imported.
    """

    import importlib

    imports_failed = set()
    for package in package_names:
        try:
            importlib.import_module(package)
        except ImportError:
            imports_failed.add(package)
    return imports_failed


def requirements_validation(component_names: List[Text]) -> None:
    """Validates that all required importable python packages are installed.

    Args:
        component_names: The list of component names.
    """

    from convo.nlu import registry

    # Validate that all required packages are installed
    imports_failed = {}
    for component_name in component_names:
        comp_class = registry.fetch_comp_class(component_name)
        packages_not_available = search_not_available_packages(
            comp_class.required_packages()
        )
        if packages_not_available:
            imports_failed[component_name] = packages_not_available
    if imports_failed:  # pragma: no cover
        map_dep_component = defaultdict(list)
        for component, missing_dependencies in imports_failed.items():
            for dependency in missing_dependencies:
                map_dep_component[dependency].append(component)

        lines_missing = [
            f"{d} (needed for {', '.join(cs)})"
            for d, cs in map_dep_component.items()
        ]
        missing = "\n  - ".join(lines_missing)
        raise DependencyExceptionMissing(
            f"Not all required importable packages are installed to use "
            f"the configured NLU pipeline. "
            f"To use this pipeline, you need to install the "
            f"missing modules: \n"
            f"  - {missing}\n"
            f"Please install the packages that contain the missing modules."
        )


def empty_pipeline_validation(pipeline: List["Element"]) -> None:
    """Ensures the pipeline is not empty.

    Args:
        pipeline: the list of the :class:`convo.nlu.components.Element`.
    """

    if len(pipeline) == 0:
        raise InvalidConfigurationError(
            "Can not train an empty pipeline. "
            "Make sure to specify a proper pipeline in "
            "the configuration using the 'pipeline' key."
        )


def only_one_tokenizer_validation(pipeline: List["Element"]) -> None:
    """Validates that only one tokenizer is present in the pipeline.

    Args:
        pipeline: the list of the :class:`convo.nlu.components.Element`.
    """

    from convo.nlu.tokenizers.tokenizer import Tokenizer

    tokens_names = []
    for component in pipeline:
        if isinstance(component, Tokenizer):
            tokens_names.append(component.name)

    if len(tokens_names) > 1:
        raise InvalidConfigurationError(
            f"The pipeline configuration contains more than one tokenizer, "
            f"which is not possible at this time. You can only use one tokenizer. "
            f"The pipeline contains the following tokenizers: {tokens_names}. "
        )


def comp_required_in_pipeline(
    required_component: Type["Element"], pipeline: List["Element"]
) -> bool:
    """Checks that required component present in the pipeline.

    Args:
        required_component: A class name of the required component.
        pipeline: The list of the :class:`convo.nlu.components.Element`.

    Returns:
        `True` if required_component is in the pipeline, `False` otherwise.
    """

    for previous_component in pipeline:
        if isinstance(previous_component, required_component):
            return True
    return False


def required_comps_validation(pipeline: List["Element"]) -> None:
    """Validates that all required components are present in the pipeline.

    Args:
        pipeline: The list of the :class:`convo.nlu.components.Element`.
    """

    for i, component in enumerate(pipeline):

        comps_missing = []
        for required_component in component.required_components():
            if not comp_required_in_pipeline(required_component, pipeline[:i]):
                comps_missing.append(required_component.name)

        comps_missing_string = ", ".join(f"'{c}'" for c in comps_missing)

        if comps_missing:
            raise InvalidConfigurationError(
                f"The pipeline configuration contains errors. The component "
                f"'{component.name}' requires {comps_missing_string} to be "
                f"placed before it in the pipeline. Please "
                f"add the required components to the pipeline."
            )


def pipeline_validation(pipeline: List["Element"]) -> None:
    """Validates the pipeline.

    Args:
        pipeline: The list of the :class:`convo.nlu.components.Element`.
    """

    empty_pipeline_validation(pipeline)
    only_one_tokenizer_validation(pipeline)
    required_comps_validation(pipeline)


def comps_in_pipeline(components: Iterable[Text], pipeline: List["Element"]):
    """Check if any of the provided components are listed in the pipeline.

    Args:
        components: A list of :class:`convo.nlu.components.Element`s to check.
        pipeline: A list of :class:`convo.nlu.components.Element`s.

    Returns:
        `True` if any of the `components` are in the `pipeline`, else `False`.

    """
    return any(any(component.name == c for component in pipeline) for c in components)


def required_comps_from_data_validation(
    pipeline: List["Element"], data: TrainingDataSet
) -> None:
    """Validates that all components are present in the pipeline based on data.

    Args:
        pipeline: The list of the :class:`convo.nlu.components.Element`s.
        data: The :class:`convo.shared.nlu.training_data.training_data.TrainingDataSet`.
    """

    if data.resp_examples and not comps_in_pipeline(
        ["ResponseSelector"], pipeline
    ):
        convo.shared.utils.io.raising_warning(
            "You have defined training data with examples for training a response "
            "selector, but your NLU pipeline does not include a response selector "
            "component. To train a model on your response selector data, add a "
            "'ResponseSelector' to your pipeline."
        )

    if data.entity_exp and not comps_in_pipeline(
        EXTRACTORS_TRAINABLE, pipeline
    ):
        convo.shared.utils.io.raising_warning(
            "You have defined training data consisting of entity examples, but "
            "your NLU pipeline does not include an entity extractor trained on "
            "your training data. To extract non-pretrained entities, add one of "
            f"{EXTRACTORS_TRAINABLE} to your pipeline."
        )

    if data.entity_exp and not comps_in_pipeline(
        {"ClassifyDIET", "CRFEntityExtractor"}, pipeline
    ):
        if data.used_entity_roles_groups():
            convo.shared.utils.io.raising_warning(
                "You have defined training data with entities that have roles/groups, "
                "but your NLU pipeline does not include a 'ClassifyDIET' or a "
                "'CRFEntityExtractor'. To train entities that have roles/groups, "
                "add either 'ClassifyDIET' or 'CRFEntityExtractor' to your "
                "pipeline."
            )

    if data.regex_features and not comps_in_pipeline(
        ["RegexFeaturizer", "ExtractRegexEntity"], pipeline
    ):
        convo.shared.utils.io.raising_warning(
            "You have defined training data with regexes, but "
            "your NLU pipeline does not include a 'RegexFeaturizer' or a "
            "'ExtractRegexEntity'. To use regexes, include either a "
            "'RegexFeaturizer' or a 'ExtractRegexEntity' in your pipeline."
        )

    if data.lookup_tables and not comps_in_pipeline(
        ["RegexFeaturizer", "ExtractRegexEntity"], pipeline
    ):
        convo.shared.utils.io.raising_warning(
            "You have defined training data consisting of lookup tables, but "
            "your NLU pipeline does not include a 'RegexFeaturizer' or a "
            "'ExtractRegexEntity'. To use lookup tables, include either a "
            "'RegexFeaturizer' or a 'ExtractRegexEntity' in your pipeline."
        )

    if data.lookup_tables:
        if not comps_in_pipeline(
            ["CRFEntityExtractor", "ClassifyDIET"], pipeline
        ):
            convo.shared.utils.io.raising_warning(
                "You have defined training data consisting of lookup tables, but "
                "your NLU pipeline does not include any components that use these "
                "features. To make use of lookup tables, add a 'ClassifyDIET' or a "
                "'CRFEntityExtractor' with the 'pattern' feature to your pipeline."
            )
        elif comps_in_pipeline(["CRFEntityExtractor"], pipeline):
            crf_comps = [c for c in pipeline if c.name == "CRFEntityExtractor"]
            # check to see if any of the possible CRFEntityExtractors will
            # featurize `pattern`
            pattern_ftr_check = False
            for crf in crf_comps:
                crf_ftrs = crf.component_config.get("features")
                # iterate through [[before],[word],[after]] features
                pattern_ftr_check = "pattern" in itertools.chain(*crf_ftrs)

            if not pattern_ftr_check:
                convo.shared.utils.io.raising_warning(
                    "You have defined training data consisting of lookup tables, but "
                    "your NLU pipeline's 'CRFEntityExtractor' does not include the "
                    "'pattern' feature. To featurize lookup tables, add the 'pattern' "
                    "feature to the 'CRFEntityExtractor' in your pipeline."
                )

    if data.entity_synonyms and not comps_in_pipeline(
        ["EntitySynonymMapper"], pipeline
    ):
        convo.shared.utils.io.raising_warning(
            "You have defined synonyms in your training data, but "
            "your NLU pipeline does not include an 'EntitySynonymMapper'. "
            "To map synonyms, add an 'EntitySynonymMapper' to your pipeline."
        )


class AbsentArgumentError(ValueError):
    """Raised when not all parameters can be filled from the context / config.

    Attributes:
        message -- explanation of which parameter is missing
    """

    def __init__(self, message: Text) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> Text:
        return self.message


class NotsupportingLanguageError(ConvoExceptions ):
    """Raised when a component is created but the language is not supported.

    Attributes:
        component -- component name
        language -- language that component doesn't support
    """

    def __init__(self, component: Text, language: Text) -> None:
        self.component = component
        self.language = language

        super().__init__(component, language)

    def __str__(self) -> Text:
        return (
            f"component '{self.component}' does not support language '{self.language}'."
        )


class ElementMetaclass(type):
    """Metaclass with `name` class property."""

    @property
    def name(cls):
        """The name property is a function of the class - its __name__."""

        return cls.__name__


class Element(metaclass=ElementMetaclass):
    """A component is a message processing unit in a pipeline.

    Components are collected sequentially in a pipeline. Each component
    is called one after another. This holds for
    initialization, training, persisting and loading the components.
    If a component comes first in a pipeline, its
    methods will be called first.

    E.g. to process an incoming message, the ``process`` method of
    each component will be called. During the processing
    (as well as the training, persisting and initialization)
    components can pass information to others components.
    The information is passed to others components by providing
    attributes to the so called pipeline context. The
    pipeline context contains all the information of the previous
    components a component can use to do its own
    processing. For example, a featurizer component can provide
    features that are used by another component down
    the pipeline to do intent classification.
    """

    # Element class name is used when integrating it in a
    # pipeline. E.g. ``[ComponentA, ComponentB]``
    # will be a proper pipeline definition where ``ComponentA``
    # is the name of the first component of the pipeline.
    @property
    def name(self) -> Text:
        """Access the class's property name from an instance."""

        return type(self).name

    # Which components are required by this component.
    # Listed components should appear before the component itself in the pipeline.
    @classmethod
    def required_components(cls) -> List[Type["Element"]]:
        """Specify which components need to be present in the pipeline.

        Returns:
            The list of class names of required components.
        """

        return []

    # Defines the default configuration parameters of a component
    # these values can be overwritten in the pipeline configuration
    # of the model. The component should choose sensible defaults
    # and should be able to create reasonable results with the defaults.
    defaults = {}

    # Defines what language(s) this component can handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None. if both `support_language_list` and
    # `not_supported_language_list` are None, it means it can handle
    # all languages. Also, only one of `support_language_list` and
    # `not_supported_language_list` can be set to not None.
    # This is an important feature for backwards compatibility of components.
    list_of_supported_langs = None

    # Defines what language(s) this component can NOT handle.
    # This attribute is designed for instance method: `can_handle_language`.
    # Default value is None. if both `support_language_list` and
    # `not_supported_language_list` are None, it means it can handle
    # all languages. Also, only one of `support_language_list` and
    # `not_supported_language_list` can be set to not None.
    # This is an important feature for backwards compatibility of components.
    list_of_not_supported_langs = None

    def __init__(self, comp_configuration: Optional[Dict[Text, Any]] = None) -> None:

        if not comp_configuration:
            comp_configuration = {}

        # makes sure the name of the configuration is part of the config
        # this is important for e.g. persistence
        comp_configuration["name"] = self.name

        self.component_config = overriding_dfault_values(self.defaults, comp_configuration)

        self.partial_processing_pipeline = None
        self.partial_processing_context = None

    @classmethod
    def required_packages(cls) -> List[Text]:
        """Specify which python packages need to be installed.

        E.g. ``["spacy"]``. More specifically, these should be
        importable python package names e.g. `sklearn` and not package
        names in the dependencies sense e.g. `scikit-learn`

        This list of requirements allows us to fail early during training
        if a required package is not installed.

        Returns:
            The list of required package names.
        """

        return []

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Optional["Metadataset"] = None,
        cached_component: Optional["Element"] = None,
        **kwargs: Any,
    ) -> "Element":
        """Load this component from file.

        After a component has been trained, it will be persisted by
        calling `persist`. When the pipeline gets loaded again,
        this component needs to be able to restore itself.
        Components can rely on any context attributes that are
        created by :meth:`components.Element.create`
        calls to components previous to this one.

        Args:
            meta: Any configuration parameter related to the model.
            model_dir: The dir to load the component from.
            model_metadata: The model's :class:`convo.nlu.model.Metadataset`.
            cached_component: The cached component.

        Returns:
            the loaded component
        """

        if cached_component:
            return cached_component

        return cls(meta)

    @classmethod
    def create(
        cls, component_config: Dict[Text, Any], config: ConvoNLUModelConfiguration
    ) -> "Element":
        """Creates this component (e.g. before a training is started).

        Method can access all configuration parameters.

        Args:
            component_config: The components configuration parameters.
            config: The model configuration parameters.

        Returns:
            The created component.
        """

        # Check language supporting
        lang = config.language
        if not cls.handle_lang(lang):
            # check failed
            raise NotsupportingLanguageError(cls.name, lang)

        return cls(component_config)

    def give_context(self) -> Optional[Dict[Text, Any]]:
        """Initialize this component for a new pipeline.

        This function will be called before the training
        is started and before the first message is processed using
        the interpreter. The component gets the opportunity to
        add information to the context that is passed through
        the pipeline during training and message parsing. Most
        components do not need to implement this method.
        It's mostly used to initialize framework environments
        like MITIE and spacy
        (e.g. loading word vectors for the pipeline).

        Returns:
            The updated component configuration.
        """

        pass

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        """Train this component.

        This is the components chance to train itself provided
        with the training data. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`convo.nlu.components.Element.create`
        of ANY component and
        on any context attributes created by a call to
        :meth:`convo.nlu.components.Element.train`
        of components previous to this one.

        Args:
            training_data:
                The :class:`convo.shared.nlu.training_data.training_data.TrainingDataSet`.
            config: The model configuration parameters.

        """

        pass

    def process(self, message: Msg, **kwargs: Any) -> None:
        """Process an incoming message.

        This is the components chance to process an incoming
        message. The component can rely on
        any context attribute to be present, that gets created
        by a call to :meth:`convo.nlu.components.Element.create`
        of ANY component and
        on any context attributes created by a call to
        :meth:`convo.nlu.components.Element.process`
        of components previous to this one.

        Args:
            message: The :class:`convo.shared.nlu.training_data.message.Msg` to process.

        """

        pass

    def persist(self, filename: Text, model_dir: Text) -> Optional[Dict[Text, Any]]:
        """Persist this component to disk for future loading.

        Args:
            filename: The file name of the model.
            model_dir: The dir to store the model to.

        Returns:
            An optional dictionary with any information about the stored model.
        """

        pass

    @classmethod
    def cache_key(
        cls, component_meta: Dict[Text, Any], model_metadata: "Metadataset"
    ) -> Optional[Text]:
        """This key is used to cache components.

        If a component is unique to a model it should return None.
        Otherwise, an instantiation of the
        component will be reused for all models where the
        metadata creates the same key.

        Args:
            component_meta: The component configuration.
            model_metadata: The component's :class:`convo.nlu.model.Metadataset`.

        Returns:
            A unique caching key.
        """

        return None

    def __getstate__(self) -> Any:
        d = self.__dict__.copy()
        # these properties should not be pickled
        if "partial_processing_context" in d:
            del d["partial_processing_context"]
        if "partial_processing_pipeline" in d:
            del d["partial_processing_pipeline"]
        return d

    def __eq__(self, others) -> bool:
        return self.__dict__ == others.__dict__

    def partial_processing_preparation(
        self, pipeline: List["Element"], context: Dict[Text, Any]
    ) -> None:
        """Sets the pipeline and context used for partial processing.

        The pipeline should be a list of components that are
        previous to this one in the pipeline and
        have already finished their training (and can therefore
        be safely used to process messages).

        Args:
            pipeline: The list of components.
            context: The context of processing.

        """

        self.partial_processing_pipeline = pipeline
        self.partial_processing_context = context

    def partially_processing(self, message:Msg) -> Msg:
        """Allows the component to process messages during
        training (e.g. external training data).

        The passed message will be processed by all components
        previous to this one in the pipeline.

        Args:
            message: The :class:`convo.shared.nlu.training_data.message.Msg` to
            process.

        Returns:
            The processed :class:`convo.shared.nlu.training_data.message.Msg`.

        """

        if self.partial_processing_context is not None:
            for component in self.partial_processing_pipeline:
                component.process(message, **self.partial_processing_context)
        else:
            log.info("Failed to run partial processing due to missing pipeline.")
        return message

    @classmethod
    def handle_lang(cls, language: Hashable) -> bool:
        """Check if component supports a specific language.

        This method can be overwritten when needed. (e.g. dynamically
        determine which language is supported.)

        Args:
            language: The language to check.

        Returns:
            `True` if component can handle specific language, `False` otherwise.
        """

        # If both `supported_language_list` and `not_supported_language_list` are set to `None`,
        # it means: support all languages
        if language is None or (
                cls.list_of_supported_langs is None
                and cls.list_of_not_supported_langs is None
        ):
            return True

        # check language supporting settings
        if cls.list_of_supported_langs and cls.list_of_not_supported_langs:
            # When user set both language supporting settings to not None, it will lead to ambiguity.
            raise ConvoExceptions (
                "Only one of `supported_language_list` and `not_supported_language_list` can be set to not None"
            )

        # convert to `list` for membership test
        lang_list_supported = (
            cls.list_of_supported_langs
            if cls.list_of_supported_langs is not None
            else []
        )
        lang_list_not_supported = (
            cls.list_of_not_supported_langs
            if cls.list_of_not_supported_langs is not None
            else []
        )

        # check if user provided a valid setting
        if not lang_list_supported and not lang_list_not_supported:
            # One of language settings must be valid (not None and not a empty list),
            # There are three combinations of settings are not valid: (None, []), ([], None) and ([], [])
            raise ConvoExceptions (
                "Empty lists for both "
                "`supported_language_list` and `not_supported language_list` "
                "is not a valid setting. If you meant to allow all languages "
                "for the component use `None` for both of them."
            )

        if lang_list_supported:
            return language in lang_list_supported
        else:
            return language not in lang_list_not_supported


D = typing.TypeVar("C", bound=Element)


class ElementBuilder:
    """Creates trainers and interpreters based on configurations.

    Caches components for reuse.
    """

    def __init__(self, use_cache: bool = True) -> None:
        self.use_cache = use_cache
        # Reuse nlp and featurizers where possible to save memory,
        # every component that implements a cache-key will be cached
        self.component_cache = {}

    def __get_cached_component(
        self, component_meta: Dict[Text, Any], model_metadata: "Metadataset"
    ) -> Tuple[Optional[Element], Optional[Text]]:
        """Load a component from the cache, if it exists.

        Returns the component, if found, and the cache key.
        """

        from convo.nlu import registry

        # try to get class name first, else create by name
        comp_name = component_meta.get("class", component_meta["name"])
        comp_class = registry.fetch_comp_class(comp_name)
        cache_key = comp_class.cache_key(component_meta, model_metadata)
        if (
            cache_key is not None
            and self.use_cache
            and cache_key in self.component_cache
        ):
            return self.component_cache[cache_key], cache_key

        return None, cache_key

    def __append_to_cache(self, component: Element, cache_key: Optional[Text]) -> None:
        """Add a component to the cache."""

        if cache_key is not None and self.use_cache:
            self.component_cache[cache_key] = component
            log.info(
                f"Added '{component.name}' to component cache. Key '{cache_key}'."
            )

    def comp_loading(
        self,
        component_meta: Dict[Text, Any],
        model_dir: Text,
        model_metadata: "Metadataset",
        **context: Any,
    ) -> Element:
        """Loads a component.

        Tries to retrieve a component from the cache, else calls
        ``load`` to create a new component.

        Args:
            component_meta:
                The metadata of the component to load in the pipeline.
            model_dir:
                The dir to read the model from.
            model_metadata (Metadataset):
                The model's :class:`convo.nlu.model.Metadataset`.

        Returns:
            The loaded component.
        """

        from convo.nlu import registry

        try:
            comp_cached, cache_key = self.__get_cached_component(
                component_meta, model_metadata
            )
            comp = registry.load_comp_by_meta(
                component_meta, model_dir, model_metadata, comp_cached, **context
            )
            if not comp_cached:
                # If the component wasn't in the cache,
                # let us add it if possible
                self.__append_to_cache(comp, cache_key)
            return comp
        except AbsentArgumentError as e:  # pragma: no cover
            raise Exception(
                f"Failed to load component from file '{component_meta.get('file')}'. "
                f"Error: {e}"
            )

    def comp_creation(
        self, component_config: Dict[Text, Any], cfg: ConvoNLUModelConfiguration
    ) -> Element:
        """Creates a component.

        Tries to retrieve a component from the cache,
        calls `create` to create a new component.

        Args:
            component_config: The component configuration.
            cfg: The model configuration.

        Returns:
            The created component.
        """

        from convo.nlu import registry
        from convo.nlu.model import Metadataset

        try:
            comp, cache_key = self.__get_cached_component(
                component_config, Metadataset(cfg.as_dictionary(), None)
            )
            if comp is None:
                comp = registry.create_comp_by_configuration(component_config, cfg)
                self.__append_to_cache(comp, cache_key)
            return comp
        except AbsentArgumentError as e:  # pragma: no cover
            raise Exception(
                f"Failed to create component '{component_config['name']}'. "
                f"Error: {e}"
            )

    def creating_comp_from_class(self, component_class: Type[D], **cfg: Any) -> D:
        """Create a component based on a class and a configuration.

        Mainly used to make use of caching when instantiating component classes."""

        component_config = {"name": component_class.name}

        return self.comp_creation(component_config, ConvoNLUModelConfiguration(cfg))
