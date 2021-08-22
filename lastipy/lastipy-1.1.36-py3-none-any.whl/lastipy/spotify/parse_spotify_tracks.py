from lastipy.track import Track
from lastipy.spotify.playlist_track import PlaylistTrack

# TODO test
def parse_tracks(json_tracks):
    return [_parse_track(json_track) for json_track in json_tracks]


def _parse_track(json_track):
    if "added_at" in json_track:
        return _parse_playlist_track(json_track)
    else:
        name, artist, track_id = _parse_common_track_properties(json_track)
        return Track(track_name=name, artist=artist, spotify_id=track_id)


def _parse_playlist_track(json_track):
    added_at = json_track["added_at"]
    if "track" in json_track:
        json_track = json_track["track"]
    name, artist, track_id = _parse_common_track_properties(json_track)
    return PlaylistTrack(
        track_name=name, artist=artist, spotify_id=track_id, added_at=added_at
    )


def _parse_common_track_properties(json_track):
    track_id = json_track["id"]
    name = json_track["name"]
    # Just getting the first artist, even if there's multiple
    artist = json_track["artists"][0]["name"]
    return name, artist, track_id
