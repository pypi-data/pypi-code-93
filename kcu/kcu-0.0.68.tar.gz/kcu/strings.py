from typing import List

def between(string: str, from_str: str, to_str: str) -> str:
    try:
        return string.split(from_str)[1].split(to_str)[0]
    except:
        return None

def split(string: str, by_substrings: List[str], keep_splitters: bool = True) -> List[str]:
    all_splitted = [string]

    for splitter in by_substrings:
        new_splitted = []

        for splitted in all_splitted:
            all_sub_splitted = splitted.split(splitter)
            i=0

            for sub_splitted in all_sub_splitted:
                if keep_splitters and i < len(all_sub_splitted) - 1:
                    sub_splitted += splitter

                new_splitted.append(sub_splitted)
                i += 1

        all_splitted = new_splitted

    return all_splitted

def to_english(s: str) -> str:
    import unicodedata

    return ''.join([c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c)])

def htmlunescape(s: str) -> str:
    import html

    try:
        return html.unescape(s)
    except:
        return s