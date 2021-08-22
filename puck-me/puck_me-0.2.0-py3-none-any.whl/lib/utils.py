from bs4 import BeautifulSoup, Tag
import pandas as pd
from bs4.element import ResultSet
import requests as req


def table_rows(soup: BeautifulSoup, table_id: str) -> ResultSet:
    table = soup.find(id=table_id)
    if table:
        table_body = table.find("tbody")
        rows = table_body.find_all("tr")
        rows = filter(lambda r: r.find("td"), rows)  # Filter headers in middle
        return rows
    return []


def read_table_to_df(soup: BeautifulSoup, table_id: str) -> pd.DataFrame:
    table = soup.find(id=table_id)
    if table:
        # Getting first because id should be unique
        table_df = pd.read_html(str(table))[0]
        return table_df
    return pd.DataFrame()


def get_soup(url: str) -> BeautifulSoup:
    r = req.get(url)
    if r.status_code == 200:
        return BeautifulSoup(r.text, "html.parser")
    else:
        raise Exception("Problem with HTTP request.")


def has_attr_with_val(tag: Tag, attr: str, val: str) -> bool:
    return tag.has_attr(attr) and tag[attr] == val


def find_data_stat(html_tag: Tag, val: str) -> Tag:
    return html_tag.find(lambda x: has_attr_with_val(x, "data-stat", val))


def parse_data_stat(html_tag: Tag, val: str, type: type):
    stat = find_data_stat(html_tag, val)
    if stat:
        stat = stat.text
    if stat:
        return type(stat)
    return None
