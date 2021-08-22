import pydantic

from classiq_interface.hybrid.result import HybridResult
from classiq_interface.generator.result import GenerationResult


class OptimizationResult(pydantic.BaseModel):
    hybrid_result: HybridResult
    generation_result: GenerationResult
