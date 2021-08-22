from puck_me.player.player import Player
from bs4.element import ResultSet
from puck_me.skater.skater_game import SkaterGame
import pandas as pd
from enum import Enum
from puck_me.lib.split_types import SplitType


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


class SkaterSplit:
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


class Skater(Player):

    ##########################
    # Public Functions
    ##########################

    def gamelog(self, year: str = None) -> list[SkaterGame]:
        if not year:
            year = self._year
        if not self._gamelog_regular_season and not self._gamelog_playoffs:
            self.__populate_gamelogs(year)
        return self._gamelog_regular_season + self._gamelog_playoffs

    def gamelog_playoffs(self, year: str = None) -> list[SkaterGame]:
        if not year:
            year = self._year
        if not self._gamelog_regular_season and not self._gamelog_playoffs:
            self.__populate_gamelogs(year)
        return self._gamelog_playoffs

    def gamelog_regular_season(self, year: str = None) -> list[SkaterGame]:
        if not year:
            year = self._year
        if not self._gamelog_regular_season and not self._gamelog_playoffs:
            self.__populate_gamelogs(year)
        return self._gamelog_regular_season

    def games_played(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.games_played

    def goals(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.goals

    def assists(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.assists

    def points(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.points

    def plus_minus(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.plus_minus

    def penalty_mins(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.penalty_minutes

    def goals_even_strength(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.goals_ev

    def goals_power_play(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.goals_pp

    def goals_short_handed(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.goals_sh

    def goals_game_winning(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.goals_gw

    def shots(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.shots

    def shooting_percentage(self, year: str = None) -> float:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.shooting_pct

    def shifts(self, year: str = None) -> int:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.shifts

    def time_on_ice_per_game(self, year: str = None) -> str:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.time_on_ice_average

    def time_on_ice_total(self, year: str = None) -> str:
        if not self._season_split or year != self._year:
            self._season_split = self.splits(SplitType.SEASON, year)[0]
        return self._season_split.time_on_ice_total

    def splits(self, split_type: SplitType, year: str = None) -> list[SkaterSplit]:
        split_df = self._split_df_lookup(year, split_type)
        return self.__split_df_to_rows(split_df)

    ##########################
    # Gamelog Section
    ##########################

    def __populate_gamelogs(self, year: str) -> None:
        if not self._gamelog_playoffs or not self._gamelog_regular_season:
            soup = self._request_player_gamelog_page(year)
            reg_season_rows = self._regular_season_games(soup)
            playoff_rows = self._playoff_games(soup)
            self._gamelog_regular_season = self.__get_games_by_table_rows(
                reg_season_rows, is_playoff=False
            )
            self._gamelog_playoffs = self.__get_games_by_table_rows(
                playoff_rows, is_playoff=True
            )

    def __get_games_by_table_rows(
        self, rows: ResultSet, is_playoff: bool
    ) -> list[SkaterGame]:
        games = []
        for row_html in rows:
            game = SkaterGame(row_html, is_playoff)
            games += [game]
        return games

    ##########################
    # Splits Section
    ##########################

    def __split_df_to_rows(self, split_df: pd.DataFrame) -> list[SkaterSplit]:
        rows = []
        for index, series in split_df.iterrows():
            rows += [SkaterSplit(series)]
        return rows
