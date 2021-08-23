import logging
from lastipy.track import Track


# TODO test
def filter_out_duplicates(tracks):
    """Filters out duplicate tracks from the given list (i.e. tracks that have the same track name and artist; see Track.are_equivalent)"""

    logging.info("Filtering out duplicates")
    logging.debug(str(len(tracks)) + " tracks before removing duplicates")
    tracks_without_duplicates = []
    # We remove duplicates with a list comprehension rather than the traditional hack of using a set, since that
    # requires the object to be hashable; plus we only want to compare the track name/artist of each track, not
    # any of the other fields (eg: Spotify ID) which might in fact differ
    [
        tracks_without_duplicates.append(track_x)
        for track_x in tracks
        if not any(
            Track.are_equivalent(track_x, track_y)
            for track_y in tracks_without_duplicates
        )
    ]
    logging.debug(str(len(tracks)) + " tracks after removing duplicates")
    return tracks_without_duplicates


# TODO test
def filter_out_tracks_in_second_list(track_list_1, track_list_2):
    """Filters out tracks from track_list_1 that are also in track_list_2"""
    filtered_tracks = [
        track_x
        for track_x in track_list_1
        if not any(Track.are_equivalent(track_x, track_y) for track_y in track_list_2)
    ]
    return filtered_tracks
