import json

import typer

from .serializers import PointSerializer
from .judge import initialize_points, simulate_game

app = typer.Typer()


@app.command()
def play_game(player1_url: str = typer.Argument(..., help="The url of the bot for player 1"),
              player2_url: str = typer.Argument(..., help="The url of the bot for player 2")):
    """
    Judge for the Bob the Builder game. Enter the endpoints for
    both the endpoints and let the judge play out the match.
    You may then go to the website and enter the game data generated
    from this tool to visualize how the game played out.
    """
    initial_pieces_list = initialize_points()
    user1_pieces = initial_pieces_list[0:2]
    user2_pieces = initial_pieces_list[2:]
    user1_initial_pieces = PointSerializer(user1_pieces, many=True).data
    user2_initial_pieces = PointSerializer(user2_pieces, many=True).data
    initial_pieces = {'player1': user1_initial_pieces, 'player2': user2_initial_pieces}
    pieces = [user1_pieces, user2_pieces]
    winner, moves, reason = simulate_game([player1_url, player2_url], pieces)
    typer.echo(
        json.dumps({'initial_pieces': initial_pieces, 'moves': moves, 'winner': winner, 'reason': reason}, indent=2))


if __name__ == '__main__':
    app()
