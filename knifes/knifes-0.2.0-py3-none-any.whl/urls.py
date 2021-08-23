
def get_url_from_text(text):
    if not text:
        return text
    start_index = text.rfind('http://')
    if start_index == -1:
        start_index = text.rfind('https://')
    if start_index == -1:
        return None
    text = text[start_index:]
    end_index = text.find(' ')
    if end_index != -1:
        return text[0:end_index]
    return text
