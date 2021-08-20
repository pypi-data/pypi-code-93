import unicodedata


def remove_tags_from_string(tags, text):
    return tags.sub('', text)


def replace_html_entities(replace_dict, text):
    for key in replace_dict:
        text = text.replace(key, replace_dict[key])
        text = text.strip()
    return text


def remove_emoji(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf8')
