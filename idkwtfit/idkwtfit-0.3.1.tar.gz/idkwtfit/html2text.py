from bs4 import BeautifulSoup


def html2text(html: str) -> str:
    """
    Returns text only extracted from html code

    >>> html = "<p>Hello</p>"
    >>> html2text(html)
    Hello

    Parameters
     - `html` (html): Html code

    Returns
     - String

    """
    soup = BeautifulSoup(html, "html.parser")
    text_parts = soup.find_all(text=True)
    return "".join(text_parts)
