from typing import List, Any
from dsframework.base.common.component import ZIDS_Component

class generatedClass(ZIDS_Component):

    def __init__(self, artifacts=None) -> None:
        super().__init__(artifacts)

    def execute(self, predictables: List[Any], **kwargs) -> List[Any]:
        return predictables
