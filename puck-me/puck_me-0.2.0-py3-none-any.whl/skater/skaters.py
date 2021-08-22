from bs4.element import Tag
from bs4 import BeautifulSoup
from puck_me.skater.skater import Skater
from puck_me.hock_ref import HockRef
from puck_me.lib import utils


class Skaters:
    @staticmethod
    def all_skaters(year: str = None) -> list[Skater]:
        skaters = []
        if not year:
            for acsii_as_int in range(97, 123):
                letter = chr(acsii_as_int)
                if letter == "x":
                    continue  # No players w last name X
                soup = Skaters.__request_letter_skater_page(letter)
                skaters += Skaters.__parse_letter_skater_soup(soup)
            return skaters
        else:
            soup = Skaters.__request_year_skater_page(year)
            ids_found = set()
            for row in utils.table_rows(soup, "stats"):
                skater = Skaters.__parse_year_skater_row(row, ids_found, year)
                if skater:
                    skaters.append(skater)
            return skaters

    #########################
    # Players by year
    #########################

    @staticmethod
    def __request_year_skater_page(year) -> BeautifulSoup:
        url = f"{HockRef.base_url}leagues/NHL_{year}_skaters.html"
        return utils.get_soup(url)

    @staticmethod
    def __parse_year_skater_row(plr_row: Tag, ids_found: set, year: str) -> Skater:
        plr_id = plr_row.find(
            lambda x: utils.has_attr_with_val(x, "data-stat", "ranker")
        ).text
        if plr_id in ids_found:
            return None
        ids_found.add(plr_id)
        name_data = plr_row.find(
            lambda x: utils.has_attr_with_val(x, "data-stat", "player")
        )
        name = name_data.text.removesuffix("*")
        url = name_data.find("a")["href"]
        skater = Skater(name, url, year)
        return skater

    ##############################
    # Players by letter of name
    ##############################

    @staticmethod
    def __request_letter_skater_page(letter) -> BeautifulSoup:
        url = f"{HockRef.base_url}players/{letter}/"
        return utils.get_soup(url)

    @staticmethod
    def __parse_letter_skater_soup(soup: BeautifulSoup) -> list[Skater]:
        skaters = []
        lines = soup.find(id="div_players").find_all("p")
        for line in lines:
            class_attr = line["class"][0]
            if class_attr != "nhl" or "G" in line.text:
                continue  # Ignore Goalies and non-nhl players
            a_tag = line.find("a")
            name = a_tag.text
            url = a_tag["href"]
            skaters += [Skater(name, url, year=None)]
        return skaters
