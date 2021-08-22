from bs4.element import Tag
from puck_me.lib import utils


class Game:
    # arena
    HOME = "Home"
    AWAY = "Away"
    # result
    WIN = "Win"
    LOSS = "Loss"
    LOSS_OT = "Loss OT"
    LOSS_SO = "Loss SO"

    def __init__(self, row_html: Tag, is_playoff: bool) -> None:
        self.__base_populate(row_html)
        self.is_playoff = is_playoff

    def __base_populate(self, row_html: Tag) -> None:
        date_game = utils.find_data_stat(row_html, "date_game")
        self.date = date_game.text
        self.__url = date_game.find("a")["href"]
        self.age = utils.find_data_stat(row_html, "age").text
        team_id = utils.find_data_stat(row_html, "team_id")
        self.team = team_id.text
        self.__team_url = team_id.find("a")["href"]
        game_location = utils.find_data_stat(row_html, "game_location").text
        self.arena = Game.AWAY if game_location == "@" else Game.HOME
        opp_id = utils.find_data_stat(row_html, "opp_id")
        self.opponent = opp_id.text
        self.__opponent_url = opp_id.find("a")["href"]
        game_result = utils.find_data_stat(row_html, "game_result").text
        self.result = Game.__map_result(game_result)
        self.is_win = self.result == Game.WIN
        self.pim = int(utils.find_data_stat(row_html, "pen_min").text)
        self.time_on_ice = utils.find_data_stat(row_html, "time_on_ice").text

    @staticmethod
    def __map_result(game_result: str) -> str:
        if game_result == "W":
            return Game.WIN
        elif game_result == "L":
            return Game.LOSS
        elif game_result == "L-OT":
            return Game.LOSS_OT
        elif game_result == "L-SO":
            return Game.LOSS_SO
