import typing
from typing import List, Optional, Text, Dict, Tuple, Union, Any
import copy
import numpy as np
from collections import defaultdict, OrderedDict
import scipy.sparse

from convo.utils.tensorflow.model_data import Data
from convo.utils.tensorflow.constants import SEQUENTIAL

if typing.TYPE_CHECKING:
    from convo.shared.nlu.training_data.features import Features

COVER = "mask"


def surface_attr(
    tracker_state_features: List[List[Dict[Text, List["Features"]]]]
) -> Dict[Text, List[List[List["Features"]]]]:
    """Restructure the input.

    Args:
        tracker_state_features: a dictionary of attributes (INTENTION, TXT, ACT_NAME,
            ACT_TEXT, ENTITIES_NAME, CONVO_SLOTS, FORM) to a list of features for all
            dialogue turns in all training trackers

    Returns:
        A dictionary of attributes to a list of features for all dialogue turns
        and all training trackers.
    """
    # collect all attributes
    attr = set(
        attribute
        for features_in_tracker in tracker_state_features
        for features_in_turn in features_in_tracker
        for attribute in features_in_turn.keys()
    )

    attr_to_features = defaultdict(list)

    for features_in_tracker in tracker_state_features:
        inter_mediate_features = defaultdict(list)

        for features_in_dialogue in features_in_tracker:
            for attribute in attr:
                # if attribute is not present in the example, populate it with None
                inter_mediate_features[attribute].append(
                    features_in_dialogue.get(attribute)
                )

        for key, value in inter_mediate_features.items():
            attr_to_features[key].append(value)

    return attr_to_features


def creating_zero_features(
    tracker_features: List[List[List["Features"]]],
) -> List["Features"]:
    # all features should have the same types
    """
    Computes default feature values for an attribute;
    Args:
        tracker_features: list containing all feature values encountered
        in the dataset for an attribute;
    """

    exp_features = next(
        iter(
            [
                list_of_features
                for turn_features in tracker_features
                for list_of_features in turn_features
                if list_of_features is not None
            ]
        )
    )

    # create zero_features for nones
    zero_ftrs = []
    for features in exp_features:
        new_ftrs = copy.deepcopy(features)
        if features.dense_check():
            new_ftrs.features = np.zeros_like(features.features)
        if features.sparse_check():
            new_ftrs.features = scipy.sparse.coo_matrix(
                features.features.shape, features.features.dtype
            )
        zero_ftrs.append(new_ftrs)

    return zero_ftrs


def conversion_to_data_format(
    tracker_state_ftrs: Union[
        List[List[Dict[Text, List["Features"]]]], List[Dict[Text, List["Features"]]]
    ],
    zero_state_ftrs: Optional[Dict[Text, List["Features"]]] = None,
) -> Tuple[Data, Optional[Dict[Text, List["Features"]]]]:
    """Converts the input into "Data" format.

    Args:
        tracker_state_ftrs: a dictionary of attributes (INTENTION, TXT, ACT_NAME,
            ACT_TEXT, ENTITIES_NAME, CONVO_SLOTS, FORM) to a list of features for all
            dialogue turns in all training trackers
        zero_state_ftrs: Contains default feature values for attributes

    Returns:
        Input in "Data" format and zero state features
    """
    train = False
    if not zero_state_ftrs:
        train = True
        zero_state_ftrs = defaultdict(list)

    # unify format of incoming features
    if isinstance(tracker_state_ftrs[0], Dict):
        tracker_state_ftrs = [[dicts] for dicts in tracker_state_ftrs]

    state_to_tracker_ftrs = surface_attr(tracker_state_ftrs)

    attr_data = {}

    # During prediction we need to iterate over the zero features attributes to
    # have all keys in the resulting model data
    if train:
        attr = list(state_to_tracker_ftrs.keys())
    else:
        attr = list(zero_state_ftrs.keys())

    # In case an attribute is not present during prediction, replace it with
    # None values that will then be replaced by zero features
    dialogue_len = 1
    for tracker_features in state_to_tracker_ftrs.values():
        dialogue_len = max(dialogue_len, len(tracker_features[0]))
    empty_ftrs = [[None] * dialogue_len]

    for attribute in attr:
        attr_data[attribute] = features_for_attr(
            attribute,
            empty_ftrs,
            state_to_tracker_ftrs,
            train,
            zero_state_ftrs,
        )

    # ensure that all attributes are in the same order
    attr_data = OrderedDict(sorted(attr_data.items()))

    return attr_data, zero_state_ftrs


def features_for_attr(
    attribute: Text,
    empty_features: List[Any],
    state_to_tracker_features: Dict[Text, List[List[List["Features"]]]],
    training: bool,
    zero_state_features: Dict[Text, List["Features"]],
) -> Dict[Text, List[np.ndarray]]:
    """Create the features for the given attribute from the tracker features.

    Args:
        attribute: the attribute
        empty_features: empty features
        state_to_tracker_features: tracker features for every state
        training: boolean indicating whether we are currently in training or not
        zero_state_features: zero features

    Returns:
        A dictionary of feature type to actual features for the given attribute.
    """
    tracker_ftrs = (
        state_to_tracker_features[attribute]
        if attribute in state_to_tracker_features
        else empty_features
    )

    # in case some features for a specific attribute and dialogue turn are
    # missing, replace them with a feature vector of zeros
    if training:
        zero_state_features[attribute] = creating_zero_features(tracker_ftrs)

    (attr_masks, _dense_ftrs, _sparse_ftrs) = map_tracking_ftrd(
        tracker_ftrs, zero_state_features[attribute]
    )

    sparse_features = defaultdict(list)
    dense_features = defaultdict(list)

    # vstack serves as removing dimension
    # TODO check vstack for sequence features
    for key, values in _sparse_ftrs.items():
        sparse_features[key] = [scipy.sparse.vstack(value) for value in values]
    for key, values in _dense_ftrs.items():
        dense_features[key] = [np.vstack(value) for value in values]

    attr_ftrs = {COVER: [np.array(attr_masks)]}

    ftr_type = set()
    ftr_type.update(list(dense_features.keys()))
    ftr_type.update(list(sparse_features.keys()))

    for feature_type in ftr_type:
        if feature_type == SEQUENTIAL:
            # TODO we don't take sequence features because that makes us deal
            #  with 4D sparse tensors
            continue

        attr_ftrs[feature_type] = []
        if feature_type in sparse_features:
            attr_ftrs[feature_type].append(
                np.array(sparse_features[feature_type])
            )
        if feature_type in dense_features:
            attr_ftrs[feature_type].append(
                np.array(dense_features[feature_type])
            )
    
    return attr_ftrs


def map_tracking_ftrd(
    tracker_features: List[List[List["Features"]]], zero_features: List["Features"]
) -> Tuple[
    List[np.ndarray],
    Dict[Text, List[List["Features"]]],
    Dict[Text, List[List["Features"]]],
]:
    """Create masks for all attributes of the given features and split the features
    into sparse and dense features.

    Args:
        tracker_features: all features
        zero_features: list of zero features

    Returns:
        - a list of attribute masks
        - a map of attribute to dense features
        - a map of attribute to sparse features
    """
    sparse_ftrs = defaultdict(list)
    dense_ftrs = defaultdict(list)
    attr_masks = []

    for turn_features in tracker_features:
        dialogue_sparse_ftrs = defaultdict(list)
        dialogue_dense_ftrs = defaultdict(list)

        # create a mask for every state
        # to capture which turn has which input
        attr_mask = np.expand_dims(np.ones(len(turn_features), np.float32), -1)

        for i, features_list in enumerate(turn_features):

            if features_list is None:
                # use zero features and set mask to zero
                attr_mask[i] = 0
                features_list = zero_features

            for features in features_list:
                # all features should have the same types
                if features.sparse_check():
                    dialogue_sparse_ftrs[features.type].append(features.features)
                else:
                    dialogue_dense_ftrs[features.type].append(features.features)

        for key, value in dialogue_sparse_ftrs.items():
            sparse_ftrs[key].append(value)
        for key, value in dialogue_dense_ftrs.items():
            dense_ftrs[key].append(value)

        attr_masks.append(attr_mask)

    return attr_masks, dense_ftrs, sparse_ftrs
