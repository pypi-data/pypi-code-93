import json
import random

import requests

from .constants import SIZE, MAX_HEIGHT, MAX_MOVES, REASONS
from .serializers import MoveSerializer, PointSerializer


# X -> row, Y -> column
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __str__(self):
        return f'Point: (x:{self.x} , y:{self.y})'


def random_point():
    x = random.randint(0, SIZE - 1)
    y = random.randint(0, SIZE - 1)
    return Point(x, y)


# generate 4 distinct random points
def initialize_points():
    points, i = [], 0
    while i < 4:
        point = random_point()
        if point not in points:
            points.append(point)
            i += 1

    return points


def validate_move_format(move):
    serializer = MoveSerializer(data=move)
    return serializer.is_valid() and move['type'] in ['MB', 'PB'] and move['index'] in [0, 1]


def get_bot_input(board, your_pieces, opponent_pieces, data):
    bot_input = {
        'board': board,
        'your_pieces': PointSerializer(your_pieces, many=True).data,
        'opponent_pieces': PointSerializer(opponent_pieces, many=True).data,
        'data': data
    }

    return bot_input


def get_next_move(bot_url, bot_input):
    try:
        response = requests.post(bot_url, json=bot_input, timeout=2)
        next_move = json.loads(response.content)
        return next_move
    except:
        return None


def convert_to_points(move):
    current_x, current_y = move['current'].values()
    to_x, to_y = move['to'].values()
    build_x, build_y = move['build'].values()
    return [Point(current_x, current_y), Point(to_x, to_y), Point(build_x, build_y)]


# check if points lie in valid range
def validate_points_range(points):
    for point in points:
        if point.x not in range(0, SIZE) or point.y not in range(0, SIZE):
            return False
    return True


# valid cell to push/move to
def validate_move_height(board, current, to):
    src_height, dest_height = board[current.x][current.y], board[to.x][to.y]
    return dest_height <= min(MAX_HEIGHT, src_height + 1)


def adjacent_cells(one, two):
    return abs(one.x - two.x) <= 1 and abs(one.y - two.y) <= 1


# destination of move is an empty cell
def empty_cell(point, pieces):
    return point not in pieces


def get_index_of_point(opp_pieces, point):
    if point not in opp_pieces:
        return -1
    return 0 if point == opp_pieces[0] else 1


def move_operation(board, pieces, turn, index, current, to):
    if pieces[turn][index] != current:
        return -1

    pieces[turn][index] = to
    return board[to.x][to.y]


def push_operation(board, pieces, turn, index, current, to):
    if adjacent_cells(pieces[turn][index], current) is False:
        return -1

    opp_index = get_index_of_point(pieces[turn ^ 1], current)
    if opp_index == -1:
        return -1

    pieces[turn ^ 1][opp_index] = to
    return board[to.x][to.y]


def validate_build_cell(src, build, pieces):
    return adjacent_cells(src, build) and build not in pieces


def build_operation(board, build):
    board[build.x][build.y] += 1
    return board[build.x][build.y]


def simulate_game(urls, pieces):
    turn, moves = 0, []
    score_sum, moves_taken, data = [0, 0], [0, 0], [None, None]
    board = [[0 for _ in range(SIZE)] for _ in range(SIZE)]
    while sum(moves_taken) < MAX_MOVES:
        bot_input = get_bot_input(board, pieces[turn], pieces[turn ^ 1], data[turn])
        move = get_next_move(urls[turn], bot_input)

        if validate_move_format(move) is False:
            return [turn ^ 1, moves, REASONS['INVALID_FORMAT_OR_TIMEOUT']]

        if 'data' in move:
            data[turn] = move['data']
            move.pop('data')

        moves.append(move)
        moves_taken[turn] += 1

        points = convert_to_points(move)
        current, to, build = points

        if (validate_points_range(points) and adjacent_cells(current, to)) is False:
            return [turn ^ 1, moves, REASONS['INVALID_POINTS']]

        if empty_cell(to, pieces[0] + pieces[1]) is False:
            return [turn ^ 1, moves, REASONS['INVALID_CELL']]

        if validate_move_height(board, current, to) is False:
            return [turn ^ 1, moves, REASONS['UNREACHABLE_CELL']]

        index = move['index']

        if move['type'] == 'MB':
            dest_height = move_operation(board, pieces, turn, index, current, to)
            if dest_height == -1:
                return [turn ^ 1, moves, REASONS['INVALID_CURRENT_MB']]

            if validate_build_cell(to, build, pieces[0] + pieces[1]) is False:
                return [turn ^ 1, moves, REASONS['INVALID_BUILD_MB']]

            new_height = build_operation(board, build)
            moves[-1]['build']['height'] = new_height

            # game over
            if dest_height == MAX_HEIGHT:
                return [turn, moves]

            # update score
            score_sum[turn] += (dest_height ** 3) / moves_taken[turn]
        else:
            dest_height = push_operation(board, pieces, turn, index, current, to)
            if dest_height == -1:
                return [turn ^ 1, moves, REASONS['INVALID_CURRENT_PB']]

            if validate_build_cell(pieces[turn][index], build, pieces[0] + pieces[1]) is False:
                return [turn ^ 1, moves, REASONS['INVALID_BUILD_PB']]

            new_height = build_operation(board, build)
            moves[-1]['build']['height'] = new_height

            if dest_height == MAX_HEIGHT:
                return [turn, moves]

        turn ^= 1

    winner = 0 if score_sum[0] > score_sum[1] else 1
    return [winner, moves, 'Game Completed!']
