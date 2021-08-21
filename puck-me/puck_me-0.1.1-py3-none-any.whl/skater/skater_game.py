from bs4.element import Tag
from puck_me.lib import utils


class SkaterGame:
    # arena
    HOME = "Home"
    AWAY = "Away"
    # result
    WIN = "Win"
    LOSS = "Loss"
    LOSS_OT = "Loss OT"
    LOSS_SO = "Loss SO"

    def __init__(self, row_html: Tag, is_playoff: bool) -> None:
        self.__populate(row_html)
        self.is_playoff = is_playoff

    def __str__(self) -> str:
        pub_dict = dict()
        for (key, value) in self.__dict__.items():
            if not key.startswith("_SkaterGame"):
                pub_dict[key] = value
        return str(pub_dict)

    def __populate(self, row_html: Tag) -> None:
        date_game = utils.find_data_stat(row_html, "date_game")
        self.date = date_game.text
        self.__url = date_game.find("a")["href"]
        self.age = utils.find_data_stat(row_html, "age").text
        team_id = utils.find_data_stat(row_html, "team_id")
        self.team = team_id.text
        self.__team_url = team_id.find("a")["href"]
        game_location = utils.find_data_stat(row_html, "game_location").text
        self.arena = SkaterGame.AWAY if game_location == "@" else SkaterGame.HOME
        opp_id = utils.find_data_stat(row_html, "opp_id")
        self.opponent = opp_id.text
        self.__opponent_url = opp_id.find("a")["href"]
        game_result = utils.find_data_stat(row_html, "game_result").text
        self.result = SkaterGame.__map_result(game_result)
        self.is_win = self.result == SkaterGame.WIN
        self.goals = int(utils.find_data_stat(row_html, "goals").text)
        self.goals_ev = int(utils.find_data_stat(row_html, "goals_ev").text)
        self.goals_pp = int(utils.find_data_stat(row_html, "goals_pp").text)
        self.goals_sh = int(utils.find_data_stat(row_html, "goals_sh").text)
        self.goals_gw = int(utils.find_data_stat(row_html, "goals_gw").text)
        self.assists = int(utils.find_data_stat(row_html, "assists").text)
        assists_ev = utils.find_data_stat(row_html, "assists_ev").text
        self.assists_ev = None if not assists_ev else assists_ev
        assists_pp = utils.find_data_stat(row_html, "assists_pp").text
        self.assists_pp = None if not assists_pp else assists_pp
        assists_sh = utils.find_data_stat(row_html, "assists_sh").text
        self.assists_sh = None if not assists_sh else assists_sh
        self.points = int(utils.find_data_stat(row_html, "points").text)
        self.plus_minus = int(utils.find_data_stat(row_html, "plus_minus").text)
        self.pim = int(utils.find_data_stat(row_html, "pen_min").text)
        self.shots = int(utils.find_data_stat(row_html, "shots").text)
        shot_pct = utils.find_data_stat(row_html, "shot_pct").text
        self.shot_pct = None if not shot_pct else float(shot_pct)
        self.shifts = int(utils.find_data_stat(row_html, "shifts").text)
        self.time_on_ice = utils.find_data_stat(row_html, "time_on_ice").text
        self.hits = int(utils.find_data_stat(row_html, "hits_all").text)
        blocks_all = utils.find_data_stat(row_html, "blocks_all").text
        self.blocks = 0 if not blocks_all else int(blocks_all)
        faceoff_wins_all = utils.find_data_stat(row_html, "faceoff_wins_all").text
        self.faceoff_wins = 0 if not faceoff_wins_all else int(faceoff_wins_all)
        faceoff_losses_all = utils.find_data_stat(row_html, "faceoff_losses_all").text
        self.faceoff_loss = 0 if not faceoff_losses_all else int(faceoff_losses_all)
        faceoff_percent = utils.find_data_stat(row_html, "faceoff_percentage_all").text
        self.faceoff_pct = None if not faceoff_percent else float(faceoff_percent)

    @staticmethod
    def __map_result(game_result: str) -> str:
        if game_result == "W":
            return SkaterGame.WIN
        elif game_result == "L":
            return SkaterGame.LOSS
        elif game_result == "L-OT":
            return SkaterGame.LOSS_OT
        elif game_result == "L-SO":
            return SkaterGame.LOSS_SO
