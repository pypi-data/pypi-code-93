#  pylint:disable=unused-argument
'''
This module defines the @modulify decorator.
'''
from typing import List, Any, Callable, Optional, cast
from soil.data_structure import DataStructure
from soil.pipeline import Pipeline
from soil.decorator import decorator
from soil.utils import generate_data_structure_ids, generate_transformation


@decorator(depth=2)
def modulify(
        _func: Optional[Callable[..., List[DataStructure]]] = None,
        *,
        output_types: Optional[Callable] = None,
        centralize: bool = False,
        distribute: bool = False,
        federating: bool = False,
        num_outputs: int = 1,
        _from_db: bool = False
) -> Callable:
    '''Decorates a function to mark it as a soil module.'''
    def modulify_decorator(fn: Callable[..., List[DataStructure]]) -> Callable:
        fnn = fn if _func is None else _func
        mod_name = fnn.__module__ + '.' + fnn.__name__
        if not _from_db and output_types is None:
            raise ValueError('@modulify: ' + mod_name + ' missing output_types')

        def decorated(*inputs: DataStructure, **kwargs: Any) -> List[DataStructure]:
            if not _from_db and output_types is not None:
                # WARNING this could fail if output_types() checks the type of *inputs
                num_outputs_in = len(output_types(*inputs, **kwargs))
            else:
                num_outputs_in = num_outputs
            new_pipeline = Pipeline.merge_pipelines(*[input.pipeline for input in inputs if input.pipeline is not None])
            output_ids = generate_data_structure_ids(mod_name, num_outputs_in)
            input_ids = [d.id if d.id is not None else d.sym_id for d in inputs]
            for i in input_ids:
                assert isinstance(i, str)
            transformation = generate_transformation(
                input_ids=cast(List[str], input_ids),
                output_ids=output_ids,
                fn_name=mod_name,
                args=kwargs
            )
            new_pipeline = new_pipeline.add_transformation(transformation)
            outputs = [
                DataStructure(sym_id=sym_id, pipeline=new_pipeline)
                for sym_id in output_ids
            ]
            return outputs
        return decorated
    if _func is None:
        return modulify_decorator
    return modulify_decorator(_func)
