import httpx
import typing as t

url = "https://api.memegen.link/images/"


meme_list = [
    'aag',
    'ackbar',
    'afraid',
    'agnes',
    'aint-got-time',
    'ams',
    'ants',
    'apcr',
    'atis',
    'away',
    'awesome',
    'awesome-awkward',
    'awkward',
    'awkward-awesome',
    'bad',
    'badchoice',
    'bd',
    'bender',
    'bihw',
    'biw',
    'blb',
    'boat',
    'both',
    'bs',
    'buzz',
    'captain',
    'captain-america',
    'cb',
    'cbg',
    'center',
    'ch',
    'cheems',
    'chosen',
    'cmm',
    'crazypills',
    'cryingfloor',
    'db',
    'dg',
    'disastergirl',
    'dodgson',
    'doge',
    'dragon',
    'drake',
    'ds',
    'dsm',
    'dwight',
    'elf',
    'ermg',
    'fa',
    'facepalm',
    'fbf',
    'feelsgood',
    'fetch',
    'fine',
    'firsttry',
    'fmr',
    'fry',
    'fwp',
    'gandalf',
    'gb',
    'gears',
    'ggg',
    'gru',
    'grumpycat',
    'hagrid',
    'happening',
    'harold',
    'hipster',
    'home',
    'icanhas',
    'imsorry',
    'inigo',
    'interesting',
    'ive',
    'iw',
    'jd',
    'jetpack',
    'joker',
    'jw',
    'keanu',
    'kermit',
    'kk',
    'kombucha',
    'leo',
    'live',
    'll',
    'lrv',
    'mb',
    'michael-scott',
    'millers',
    'mini-keanu',
    'mmm',
    'money',
    'mordor',
    'morpheus',
    'mouth',
    'mw',
    'nice',
    'noidea',
    'ntot',
    'oag',
    'officespace',
    'older',
    'oprah',
    'patrick',
    'persian',
    'philosoraptor',
    'pigeon',
    'ptj',
    'puffin',
    'red',
    'regret',
    'remembers',
    'reveal',
    'right',
    'rollsafe',
    'sad-biden',
    'sad-boehner',
    'sad-bush',
    'sad-clinton',
    'sad-obama',
    'sadfrog',
    'saltbae',
    'same',
    'sarcasticbear',
    'sb',
    'scc',
    'sf',
    'sk',
    'ski',
    'snek',
    'soa',
    'sohappy',
    'sohot',
    'soup-nazi',
    'sparta',
    'spiderman',
    'spongebob',
    'ss',
    'stew',
    'stonks',
    'stop-it',
    'success',
    'tenguy',
    'toohigh',
    'tried',
    'trump',
    'ugandanknuck',
    'whatyear',
    'winter',
    'wkh',
    'wonka',
    'worst',
    'xy',
    'yallgot',
    'yodawg',
    'yuno',
    'zero-wing',
]


def get_meme(name: str, down: str, up: t.Optional[str] = None):

    if name not in meme_list:
        raise Exception(f"Sorry we don't have meme pic named {name} yet.")

    base = url + name
    full: str
    # upndown = [up, down]
    caps = []
    for w in [up, down]:
        if not w:
            continue
        _ = (
            w.replace(" ", "_")
            .replace("?", "~q")
            .replace("&", "~h")
            .replace("#", "~a")
            .replace("'", '"')
        )
        caps.append(_)

    if len(caps) == 2:
        up, down = caps
        full = f"{base}/{up}/{down}.jpg"
    elif len(caps) == 1:
        down = caps[0]
        full = f"{base}/_/{down}.jpg"
    else:
        raise Exception("One meme goes with two lines: Up and Down")

    with httpx.stream("GET", full) as r:
        with open(f"{name}.jpg", 'wb+') as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
