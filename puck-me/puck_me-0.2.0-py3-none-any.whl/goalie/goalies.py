from bs4.element import Tag
from bs4 import BeautifulSoup
from puck_me.goalie.goalie import Goalie
from puck_me.hock_ref import HockRef
from puck_me.lib import utils


class Goalies:
    @staticmethod
    def all_goalies(year: str = None) -> list[Goalie]:
        goalies = []
        if not year:
            for acsii_as_int in range(97, 123):
                letter = chr(acsii_as_int)
                if letter == "x":
                    continue  # No players w last name X
                soup = Goalies.__request_letter_player_page(letter)
                goalies += Goalies.__parse_letter_goalie_soup(soup)
            return goalies
        else:
            soup = Goalies.__request_year_goalie_page(year)
            ids_found = set()
            for row in utils.table_rows(soup, "stats"):
                goalie = Goalies.__parse_year_goalie_row(row, ids_found, year)
                if goalie:
                    goalies.append(goalie)
            return goalies

    #########################
    # Goalies by year
    #########################

    @staticmethod
    def __request_year_goalie_page(year) -> BeautifulSoup:
        url = f"{HockRef.base_url}leagues/NHL_{year}_goalies.html"
        return utils.get_soup(url)

    @staticmethod
    def __parse_year_goalie_row(plr_row: Tag, ids_found: set, year: str) -> Goalie:
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
        goalie = Goalie(name, url, year)
        return goalie

    ##############################
    # Players by letter of name
    ##############################

    @staticmethod
    def __request_letter_player_page(letter) -> BeautifulSoup:
        url = f"{HockRef.base_url}players/{letter}/"
        return utils.get_soup(url)

    @staticmethod
    def __parse_letter_goalie_soup(soup: BeautifulSoup) -> list[Goalie]:
        goalies = []
        lines = soup.find(id="div_players").find_all("p")
        for line in lines:
            class_attr = line["class"][0]
            if class_attr != "nhl" or "G" not in line.text:
                continue  # Ignore Skaters and non-nhl players
            a_tag = line.find("a")
            name = a_tag.text
            url = a_tag["href"]
            goalies += [Goalie(name, url, year=None)]
        return goalies
