from typing import Dict, List

from pydantic import root_validator

from .. import Annotation, ResponseObject


class AnnotationsResponse(ResponseObject):
    """
    Response representing standoff annotations over a single stream of data (e.g. information extraction results).

    Attributes
    ----------
    type (string, required): type of response
    warnings (List[StatusMessage], optional): messages describing any warnings on responses
    features (dict, optional): arbitrary json metadata about content
    annotations (Dict[str, List[Annotation]], optional): optional annotations on request
    """

    type: str = "annotations"
    features: dict = None
    annotations: Dict[str, List[Annotation]] = None

    @root_validator()
    def either_features_or_annotations(cls, values):
        """ "
        validator: ensures either the "features" or "annotations" fields are present
        """
        features, annotations = values.get("features"), values.get("annotations")
        if features is None and annotations is None:
            raise ValueError('A annotation response must have either "features" or "annotations" fields')
        return values

    def auto_content(self):
        if self.warnings is not None:
            return self.dict()
        if self.features is not None:
            return self.dict()
        if len(self.annotations) == 1:
            return self.dict()["annotations"][0]
        return self.dict()["annotations"]
