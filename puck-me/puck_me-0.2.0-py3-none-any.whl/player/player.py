from bs4.element import Comment, ResultSet
from puck_me.hock_ref import HockRef
from bs4 import BeautifulSoup
from puck_me.lib import utils
from puck_me.skater.skater_game import SkaterGame
import pandas as pd
from enum import Enum
from puck_me.lib.split_types import SplitType


class Player:
    def __init__(self, name: str, url: str, year: str) -> None:
        self.__plr_base_url = url[1:].removesuffix(".html")
        self._gamelog_regular_season = []
        self._gamelog_playoffs = []
        self._split_dfs_dict = dict()
        self._season_split = None
        self._year = year
        self.name = name

    ##########################
    # Gamelog Section
    ##########################

    def _request_player_gamelog_page(self, year: str) -> BeautifulSoup:
        url = f"{HockRef.base_url}{self.__plr_base_url}/gamelog/{year}"
        return utils.get_soup(url)

    def _regular_season_games(self, soup: BeautifulSoup) -> ResultSet:
        table_id = "gamelog"
        return utils.table_rows(soup, table_id)

    def _playoff_games(self, soup: BeautifulSoup) -> ResultSet:
        table_id = "gamelog_playoffs"
        table = soup.find(id="all_gamelog_playoffs")
        if table:  # False if no playoff games
            # Playoff table is in comments. Need to parse the comments as soup
            for element in table(text=lambda text: isinstance(text, Comment)):
                soup = BeautifulSoup(element, "html.parser")
            return utils.table_rows(soup, table_id)
        return []

    ##########################
    # Splits Section
    ##########################

    def __request_player_splits_page(self, year: str) -> BeautifulSoup:
        url = f"{HockRef.base_url}{self.__plr_base_url}/splits/{year}"
        return utils.get_soup(url)

    def __get_splits_df(self, year: str) -> pd.DataFrame:
        soup = self.__request_player_splits_page(year)
        splits_df = utils.read_table_to_df(soup, table_id="splits")
        if not splits_df.empty:
            # Filter header rows in middle of table
            first_col = splits_df.columns.values[0]
            splits_df = splits_df[splits_df[first_col] != first_col]
        return splits_df

    def __populate_split_dfs(self, year: str) -> None:
        if not year:
            raise Exception("Year must be specified.")
        split_col = "Split"
        df = self.__get_splits_df(year)
        if df.empty:
            raise ValueError(
                f"No table found for {self.name}'s {year} splits. Check if year is valid."
            )
        curr_table = "Season"
        curr_rows = []
        df_dict = dict()
        for index, row in df.iterrows():
            if str(row.loc[split_col]) != "nan":
                df_dict[curr_table] = pd.DataFrame(curr_rows)
                curr_table = row.loc[split_col]
                curr_rows = [row]
            else:
                curr_rows += [row]
        df_dict[curr_table] = pd.DataFrame(curr_rows)
        curr_table = row.loc[split_col]
        curr_rows = [row]
        self._split_dfs_dict[year] = df_dict

    def _split_df_lookup(
        self,
        year: str,
        split_type: SplitType,
    ) -> pd.DataFrame:
        if not year:
            year = self._year
        if not self._split_dfs_dict or year not in self._split_dfs_dict.keys():
            self.__populate_split_dfs(year)
        return self._split_dfs_dict[year][split_type.value]

    ##########################
    # Main Section
    ##########################

    def _request_player_main_page(self) -> BeautifulSoup:
        url = f"{HockRef.base_url}{self.__plr_base_url}.html"
        return utils.get_soup(url)
