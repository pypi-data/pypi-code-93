def parse_track_name(json_track):
    return json_track["name"]


def parse_artist(json_track):
    artist_json = json_track["artist"]
    if "name" in artist_json:
        artist = artist_json["name"]
    elif "#text" in artist_json:
        artist = artist_json["#text"]
    return artist
