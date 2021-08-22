from bs4.element import Comment
from pandas.core import series
from puck_me.hock_ref import HockRef
from bs4 import BeautifulSoup
from puck_me.lib import utils
from puck_me.skater.skater_game import SkaterGame
import pandas as pd
from enum import Enum


class SplitType(Enum):
    SEASON = "Season"
    ARENA = "Place"
    ALL_STAR = "All_Star"
    RESULT = "Result"
    MONTH = "Month"
    CONFERENCE = "Conference"
    DIVISION = "Division"
    OPPONENT = "Opponent"


class SplitCol(Enum):
    VALUE = "Value"
    GAMES_PLAYED = "GP"
    GOALS = "G"
    ASSISTS = "A"
    POINTS = "PTS"
    PLUS_MINUS = "+/-"
    PENALTY_MINS = "PIM"
    GOALS_EV = "EV"
    GOALS_PP = "PP"
    GOALS_SH = "SH"
    GOALS_GW = "GW"
    SHOTS = "S"
    SHOOTING_PCT = "S%"
    SHIFTS = "SHFT"
    TIME_ON_ICE = "TOI"
    TIME_ON_ICE_AVG = "ATOI"


class Split:
    def __init__(self, split_table_series: pd.Series) -> None:
        self.value = split_table_series[SplitCol.VALUE.value]
        self.games_played = split_table_series[SplitCol.GAMES_PLAYED.value]
        self.goals = split_table_series[SplitCol.GOALS.value]
        self.assists = split_table_series[SplitCol.ASSISTS.value]
        self.points = split_table_series[SplitCol.POINTS.value]
        self.plus_minus = split_table_series[SplitCol.PLUS_MINUS.value]
        self.penalty_minutes = split_table_series[SplitCol.PENALTY_MINS.value]
        self.goals_ev = split_table_series[SplitCol.GOALS_EV.value]
        self.goals_pp = split_table_series[SplitCol.GOALS_PP.value]
        self.goals_sh = split_table_series[SplitCol.GOALS_SH.value]
        self.goals_gw = split_table_series[SplitCol.GOALS_GW.value]
        self.shots = split_table_series[SplitCol.SHOTS.value]
        self.shooting_pct = split_table_series[SplitCol.SHOOTING_PCT.value]
        self.shifts = split_table_series[SplitCol.SHIFTS.value]
        self.time_on_ice_total = split_table_series[SplitCol.TIME_ON_ICE.value]
        self.time_on_ice_average = split_table_series[SplitCol.TIME_ON_ICE_AVG.value]


class Skater:
    def __init__(self, name: str, url: str, year: str) -> None:
        self.__plr_base_url = url[1:].removesuffix(".html")
        self.__gamelog_regular_season = []
        self.__gamelog_playoffs = []
        self.__split_dfs_dict = dict()
        self.__season_split = None
        self.__year = year
        self.name = name

    ##########################
    # Public Functions
    ##########################

    def gamelog(self, year: str = None) -> list[SkaterGame]:
        if not year:
            year = self.__year
        if not self.__gamelog_regular_season and not self.__gamelog_playoffs:
            self.__populate_gamelogs(year)
        return self.__gamelog_regular_season + self.__gamelog_playoffs

    def gamelog_playoffs(self, year: str = None) -> list[SkaterGame]:
        if not year:
            year = self.__year
        if not self.__gamelog_regular_season and not self.__gamelog_playoffs:
            self.__populate_gamelogs(year)
        return self.__gamelog_playoffs

    def gamelog_regular_season(self, year: str = None) -> list[SkaterGame]:
        if not year:
            year = self.__year
        if not self.__gamelog_regular_season and not self.__gamelog_playoffs:
            self.__populate_gamelogs(year)
        return self.__gamelog_regular_season

    def games_played(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.games_played

    def goals(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.goals

    def assists(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.assists

    def points(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.points

    def plus_minus(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.plus_minus

    def penalty_mins(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.penalty_minutes

    def goals_even_strength(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.goals_ev

    def goals_power_play(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.goals_pp

    def goals_short_handed(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.goals_sh

    def goals_game_winning(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.goals_gw

    def shots(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.shots

    def shooting_percentage(self, year: str = None) -> float:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.shooting_pct

    def shifts(self, year: str = None) -> int:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.shifts

    def time_on_ice_per_game(self, year: str = None) -> str:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.time_on_ice_average

    def time_on_ice_total(self, year: str = None) -> str:
        if not self.__season_split or year != self.__year:
            self.__season_split = self.splits(SplitType.SEASON, year)[0]
        return self.__season_split.time_on_ice_total

    def splits(self, split_type: SplitType, year: str = None) -> list[Split]:
        split_df = self.__split_df_lookup(year, split_type)
        return self.__split_df_to_rows(split_df)

    ##########################
    # Gamelog Section
    ##########################

    def __populate_gamelogs(self, year: str) -> None:
        if not self.__gamelog_playoffs or not self.__gamelog_regular_season:
            soup = self.__request_skater_gamelog_page(year)
        self.__gamelog_regular_season = self.__regular_season_games(soup)
        self.__gamelog_playoffs = self.__playoff_games(soup)

    def __regular_season_games(self, soup: BeautifulSoup) -> list[SkaterGame]:
        table_id = "gamelog"
        return self.__get_games_by_table_name(soup, table_id, is_playoff=False)

    def __playoff_games(self, soup: BeautifulSoup) -> list[SkaterGame]:
        table_id = "gamelog_playoffs"
        table = soup.find(id="all_gamelog_playoffs")
        if table:  # False if no playoff games
            # Playoff table is in comments. Need to parse the comments as soup
            for element in table(text=lambda text: isinstance(text, Comment)):
                soup = BeautifulSoup(element, "html.parser")
            return self.__get_games_by_table_name(soup, table_id, is_playoff=True)
        return []

    def __request_skater_gamelog_page(self, year: str) -> BeautifulSoup:
        url = f"{HockRef.base_url}{self.__plr_base_url}/gamelog/{year}"
        return utils.get_soup(url)

    def __get_games_by_table_name(
        self, soup: BeautifulSoup, table_id: str, is_playoff: bool
    ) -> list[SkaterGame]:
        rows = utils.table_rows(soup, table_id)
        games = []
        for row_html in rows:
            game = SkaterGame(row_html, is_playoff)
            games += [game]
        return games

    ##########################
    # Splits Section
    ##########################

    def __get_splits_df(self, year: str) -> pd.DataFrame:
        soup = self.__request_skater_splits_page(year)
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
        self.__split_dfs_dict[year] = df_dict

    def __request_skater_splits_page(self, year: str) -> BeautifulSoup:
        url = f"{HockRef.base_url}{self.__plr_base_url}/splits/{year}"
        return utils.get_soup(url)

    def __split_df_lookup(
        self,
        year: str,
        split_type: SplitType,
    ) -> pd.DataFrame:
        if not year:
            year = self.__year
        if not self.__split_dfs_dict or year not in self.__split_dfs_dict.keys():
            self.__populate_split_dfs(year)
        return self.__split_dfs_dict[year][split_type.value]

    def __split_df_to_rows(self, split_df: pd.DataFrame) -> list[Split]:
        rows = []
        for index, series in split_df.iterrows():
            rows += [Split(series)]
        return rows

    ##########################
    # Main Page Section
    ##########################

    def __request_skater_main_page(self) -> BeautifulSoup:
        url = f"{HockRef.base_url}{self.__plr_base_url}.html"
        return utils.get_soup(url)
