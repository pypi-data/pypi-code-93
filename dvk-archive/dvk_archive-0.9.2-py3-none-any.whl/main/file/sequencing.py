#!/usr/bin/env python3

from dvk_archive.main.file.dvk_handler import DvkHandler
from typing import List

def set_sequence(dvk_handler:DvkHandler=None,
                indexes:List[int]=[],
                seq_title:str=None):
    """
    Sets a group of Dvks as a sequence.

    :param dvk_handler: DvkHandler used to source Dvks, defaults to None
    :type dvk_handler: DvkHandler, optional
    :param indexes: Indexes of the Dvks to put in sequence, defaults to None
    :type indexes: list[int], optional
    :param seq_title: Sequence title for Dvk if desired, defaults to None
    :type seq_title: str, optional
    """
    if (dvk_handler is not None
                and indexes is not None
                and len(indexes) > 0):
        for i in range(0, len(indexes)):
            # Get Dvk to edit from index
            edit_dvk = dvk_handler.get_dvk(indexes[i])
            # Set the previous ID
            if i == 0:
                # Set to first if first in the sequence
                edit_dvk.set_first()
            else:
                prev_dvk = dvk_handler.get_dvk(indexes[i-1])
                edit_dvk.set_prev_id(prev_dvk.get_dvk_id())
            # Set the next ID
            if i == len(indexes) - 1:
                # Set to last if last in the sequence
                edit_dvk.set_last()
            else:
                next_dvk = dvk_handler.get_dvk(indexes[i+1])
                edit_dvk.set_next_id(next_dvk.get_dvk_id())
            # Set the sequence title
            if len(indexes) > 1:
                edit_dvk.set_sequence_title(seq_title)
            else:
                edit_dvk.set_sequence_title()
            # Write Dvk and update the DvkHandler
            edit_dvk.write_dvk()
            dvk_handler.set_dvk(edit_dvk, indexes[i])

def get_sequence(dvk_handler:DvkHandler=None, index:int=None) -> List[int]:
    """
    Gets a group of Dvks in a sequence from a given starting index.

    :param dvk_handler: DvkHandler to search through for Dvks, defaults to None
    :type dvk_handler: DvkHandler, optional
    :param index: Index of a Dvk in she sequence, defaults to None
    :type index: int, optional
    :return: List of indexes for the Dvks in the sequence
    :rtype: list[int]
    """
    try:
        # Get all Dvks from after the given index
        next_ids = []
        if index > -1:
            dvk = dvk_handler.get_dvk(index)
        while not dvk.is_last() and dvk.get_next_id() is not None:
            # Get next Dvk
            next_id = dvk.get_next_id()
            cur_index = dvk_handler.get_dvk_by_id(next_id)
            if cur_index == -1 or cur_index in next_ids:
                # Stop if Dvk doesn't exist or is already in sequence
                break
            next_ids.append(cur_index)
            dvk = dvk_handler.get_dvk(cur_index)
        # Get all Dvks from before the given index
        ids = []
        dvk = dvk_handler.get_dvk(index)
        while not dvk.is_first() and dvk.get_prev_id() is not None:
            # Get prev Dvk
            prev_id = dvk.get_prev_id()
            cur_index = dvk_handler.get_dvk_by_id(prev_id)
            if cur_index == -1 or cur_index in ids:
                # Stop if Dvk doesn't exist or is already in sequence
                break
            ids.append(cur_index)
            dvk = dvk_handler.get_dvk(cur_index)
        ids.reverse()
        # Combine lists of indexes
        ids.append(index)
        ids.extend(next_ids)
        return ids
    except:
        return []
