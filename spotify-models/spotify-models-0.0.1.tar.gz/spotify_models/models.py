from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from iso3166 import Country


@dataclass
class Track:
    album: Album
    artists: list[Artist]
    disc_number: int
    duration_ms: int
    explicit: bool
    href: str
    spotify_id: str
    is_local: bool
    name: str
    popularity: int
    track_number: int
    uri: str

    available_markets: list[Country] = None
    external_ids: dict[str, str] = None
    external_urls: dict[str, str] = None
    is_playable: bool = None
    linked_from: bool = None
    preview_url: str = None
    restrictions: list[str] = None


@dataclass
class Artist:
    external_urls: dict[str, str]
    followers: int  # FIXME?
    genres: list[Genre]
    href: str
    spotify_id: str
    images: list[ImageRef]
    name: str
    popularity: int
    uri: str


class AlbumType(Enum):
    SINGLE = "single"
    ALBUM = "album"


@dataclass
class Album:
    album_type: AlbumType
    artists: list[Artist]
    available_markets: list[Country]
    copyrights: dict[str, str]
    external_ids: dict[str, str]
    external_urls: dict[str, str]
    genres: list[Genre]
    href: str
    spotify_id: str
    images: list[ImageRef]
    name: str
    popularity: int
    release_date: datetime
    tracks: list[Track]
    uri: str


class ImageRef:
    height: int
    width: int
    url: str


class Genre(Enum):
    ACOUSTIC = "acoustic"
    AFROBEAT = "afrobeat"
    ALT_ROCK = "alt-rock"
    ALTERNATIVE = "alternative"
    AMBIENT = "ambient"
    ANIME = "anime"
    BLACK_METAL = "black-metal"
    BLUEGRASS = "bluegrass"
    BLUES = "blues"
    BOSSANOVA = "bossanova"
    BRAZIL = "brazil"
    BREAKBEAT = "breakbeat"
    BRITISH = "british"
    CANTOPOP = "cantopop"
    CHICAGO_HOUSE = "chicago-house"
    CHILDREN = "children"
    CHILL = "chill"
    CLASSICAL = "classical"
    CLUB = "club"
    COMEDY = "comedy"
    COUNTRY = "country"
    DANCE = "dance"
    DANCEHALL = "dancehall"
    DEATH_METAL = "death-metal"
    DEEP_HOUSE = "deep-house"
    DETROIT_TECHNO = "detroit-techno"
    DISCO = "disco"
    DISNEY = "disney"
    DRUM_AND_BASS = "drum-and-bass"
    DUB = "dub"
    DUBSTEP = "dubstep"
    EDM = "edm"
    ELECTRO = "electro"
    ELECTRONIC = "electronic"
    EMO = "emo"
    FOLK = "folk"
    FORRO = "forro"
    FRENCH = "french"
    FUNK = "funk"
    GARAGE = "garage"
    GERMAN = "german"
    GOSPEL = "gospel"
    GOTH = "goth"
    GRINDCORE = "grindcore"
    GROOVE = "groove"
    GRUNGE = "grunge"
    GUITAR = "guitar"
    HAPPY = "happy"
    HARD_ROCK = "hard-rock"
    HARDCORE = "hardcore"
    HARDSTYLE = "hardstyle"
    HEAVY_METAL = "heavy-metal"
    HIP_HOP = "hip-hop"
    HOLIDAYS = "holidays"
    HONKY_TONK = "honky-tonk"
    HOUSE = "house"
    IDM = "idm"
    INDIAN = "indian"
    INDIE = "indie"
    INDIE_POP = "indie-pop"
    INDUSTRIAL = "industrial"
    IRANIAN = "iranian"
    J_DANCE = "j-dance"
    J_IDOL = "j-idol"
    J_POP = "j-pop"
    J_ROCK = "j-rock"
    JAZZ = "jazz"
    K_POP = "k-pop"
    KIDS = "kids"
    LATIN = "latin"
    LATINO = "latino"
    MALAY = "malay"
    MANDOPOP = "mandopop"
    METAL = "metal"
    METAL_MISC = "metal-misc"
    METALCORE = "metalcore"
    MINIMAL_TECHNO = "minimal-techno"
    MOVIES = "movies"
    MPB = "mpb"
    NEW_AGE = "new-age"
    NEW_RELEASE = "new-release"
    OPERA = "opera"
    PAGODE = "pagode"
    PARTY = "party"
    PHILIPPINES_OPM = "philippines-opm"
    PIANO = "piano"
    POP = "pop"
    POP_FILM = "pop-film"
    POST_DUBSTEP = "post-dubstep"
    POWER_POP = "power-pop"
    PROGRESSIVE_HOUSE = "progressive-house"
    PSYCH_ROCK = "psych-rock"
    PUNK = "punk"
    PUNK_ROCK = "punk-rock"
    R_N_B = "r-n-b"
    RAINY_DAY = "rainy-day"
    REGGAE = "reggae"
    REGGAETON = "reggaeton"
    ROAD_TRIP = "road-trip"
    ROCK = "rock"
    ROCK_N_ROLL = "rock-n-roll"
    ROCKABILLY = "rockabilly"
    ROMANCE = "romance"
    SAD = "sad"
    SALSA = "salsa"
    SAMBA = "samba"
    SERTANEJO = "sertanejo"
    SHOW_TUNES = "show-tunes"
    SINGER_SONGWRITER = "singer-songwriter"
    SKA = "ska"
    SLEEP = "sleep"
    SONGWRITER = "songwriter"
    SOUL = "soul"
    SOUNDTRACKS = "soundtracks"
    SPANISH = "spanish"
    STUDY = "study"
    SUMMER = "summer"
    SWEDISH = "swedish"
    SYNTH_POP = "synth-pop"
    TANGO = "tango"
    TECHNO = "techno"
    TRANCE = "trance"
    TRIP_HOP = "trip-hop"
    TURKISH = "turkish"
    WORK_OUT = "work-out"
    WORLD_MUSIC = "world-music"
