from bs4 import BeautifulSoup


def clean_up_string(s):  # to clean up unnecessary html tags &amp .etc
    if not s:
        return s
    try:
        clean_text = BeautifulSoup(str(s), 'html.parser').text
        return clean_text.strip()
    except Exception as  e:
        print(s)
        return s

def clean_up_string_2(s):  # to clean up unnecessary html tags &amp .etc
    if not s:
        return s
    try:
        clean_text = str(s).replace('&amp;', '&').replace('&#39;', '\'')
        return clean_text.strip()
    except Exception as e:
        print(s)
        return s
