from cytoolz.curried import filter, map
from cytoolz.functoolz import compose
from cytoolz.itertoolz import concat

from genomoncology.parse.ensures import ensure_collection
from genomoncology.pipeline.converters import non_null
from genomoncology.pipeline.transformers import get_in_field, transform


def calls_to_alterations(calls):
    calls = ensure_collection(calls)
    pipeline = compose(
        concat, filter(non_null), map(get_in_field("annotations.alteration"))
    )
    alterations = list(pipeline(calls))
    return alterations


def transform_match_response(response, default_spec):
    transformer = transform(default_spec)

    # handle either model or dict version of response
    # contents -> object  //  everything else -> dict
    results = getattr(response, "results", None)
    results = results or response.get("results")

    transformed = map(transformer, results)
    return transformed
