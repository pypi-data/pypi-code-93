from bs4.element import Tag
from puck_me.lib import utils
from puck_me.game.game import Game


class SkaterGame(Game):
    def __init__(self, row_html: Tag, is_playoff: bool) -> None:
        super().__init__(row_html, is_playoff)
        self.__populate_skater_stats(row_html)

    def __str__(self) -> str:
        pub_dict = dict()
        for (key, value) in self.__dict__.items():
            if not key.startswith("_SkaterGame"):
                pub_dict[key] = value
        return str(pub_dict)

    def __populate_skater_stats(self, row_html: Tag) -> None:
        self.goals = utils.parse_data_stat(row_html, "goals", int)
        self.goals_ev = utils.parse_data_stat(row_html, "goals_ev", int)
        self.goals_pp = utils.parse_data_stat(row_html, "goals_pp", int)
        self.goals_sh = utils.parse_data_stat(row_html, "goals_sh", int)
        self.goals_gw = utils.parse_data_stat(row_html, "goals_gw", int)
        self.assists = utils.parse_data_stat(row_html, "assists", int)
        self.assists_ev = utils.parse_data_stat(row_html, "assists_ev", int)
        self.assists_pp = utils.parse_data_stat(row_html, "assists_pp", int)
        self.assists_sh = utils.parse_data_stat(row_html, "assists_sh", int)
        self.points = utils.parse_data_stat(row_html, "points", int)
        self.plus_minus = utils.parse_data_stat(row_html, "plus_minus", int)
        self.shots = utils.parse_data_stat(row_html, "shots", int)
        self.shot_pct = utils.parse_data_stat(row_html, "shot_pct", float)
        self.shifts = utils.parse_data_stat(row_html, "shifts", int)
        self.hits = utils.parse_data_stat(row_html, "hits_all", int)
        self.blocks = utils.parse_data_stat(row_html, "blocks_all", int)
        self.faceoff_wins = utils.parse_data_stat(row_html, "faceoff_wins_all", int)
        self.faceoff_loss = utils.parse_data_stat(row_html, "faceoff_losses_all", int)
        self.faceoff_pct = utils.parse_data_stat(
            row_html, "faceoff_percentage_all", float
        )
