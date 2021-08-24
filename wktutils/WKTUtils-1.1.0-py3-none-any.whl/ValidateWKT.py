import shapely
from typing import Union, List, Tuple


def recurseShapes(shapely_shapes: shapely.geometry) -> list:
    # If you can't iterate on it, it's a base shape. Return it:
    if not hasattr(shapely_shapes, "__iter__"):
        return [shapely_shapes]
    # recurse through each index, to break apart list(list(list( ... ))) type scenarios:
    else:
        base_list = []
        for shape in shapely_shapes:
            base_shapes = recurseShapes(shape)
            base_list.extend(base_shapes)
        return base_list

# Can take a wkt, or list of wkt's, and will
#    1) output a single wkt, with as few "geocollections" as possible (Breaks apart GeometryCollections, MultiPolygons, etc)
#    2) populate errors (bad input), but for that element in "wkts" ONLY. (Will still chug along on the rest)
# Returns: str WKT, list of Errors.
#    Each element in 'wkts' can create it's own error, others won't be affected.
#    If no valid shapes are found, a "GeometryCollection EMPTY" is returned. Else "GeometryCollection( shape(s) )" is.
#    If no errors, an empty list will still be returned in the second return slot.
def validateWKT(wkts: Union[str, List[str]]) -> Tuple[str, List[str]]:
    # If not a list, make a list of a single wkt:
    if not isinstance(wkts, list):
        wkts = [wkts]

    # Either the wkt is added to valid_wkt's as a shapely object, or it errors out and the message is added to 'errors'.
    valid_wkts = []
    errors = []
    for i in range(len(wkts)):
        single_wkt = wkts[i]
        if not isinstance(single_wkt, str):
            errors.append("ValidateWKT: A 'wkt' was passed in to validate, that was not a string. Type: '{0}'. Index: '{1}'.".format(type(single_wkt), i) )
            continue

        # Switch elements in list to shapely objects:
        try:
            single_wkt = shapely.wkt.loads(single_wkt)
        except Exception as e:
            errors.append("ValidateWKT: Shapely failed to load wkt. (Is it formatted correctly?). Index: '{0}'. Error: '{1}'.".format(i, str(e)))
            continue
        # Add the shapely objects to the new list:
        valid_wkts.append(single_wkt)

    # Go through, breaking out GeometryCollections, MultiPolygons, etc, to basic shape components:
    basic_shapes = []
    for shape in valid_wkts:
        basic_list = recurseShapes(shape)
        basic_shapes.extend(basic_list)
    
    # Turn back into string wkt's, now that they're verified:
    basic_shapes = [shapely.wkt.dumps(myWKT) for myWKT in basic_shapes]

    # Return a GeometryCollection of all your basic shapes:
    return_wkt = "GeometryCollection"
    if len(basic_shapes) == 0:
        return_wkt += " EMPTY"
    else:
        return_wkt += "({0})".format(",".join(basic_shapes))
    return return_wkt, errors