from typing import Dict
from typing import List

from tecton_proto.data.transformation_pb2 import Transformation
from tecton_spark.id_helper import IdHelper


def get_transformation_id2proto_map(transformations: List[Transformation]) -> Dict[str, Transformation]:
    """
    Returns a ID string -> Transformation proto map.
    """
    return {IdHelper.to_string(t.transformation_id): t for t in transformations}
