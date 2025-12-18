# player_sequence = 0w01b2
from typing import Sequence
import numpy as np
import time
from numpy.lib import _array_utils_impl
from Bots.ChessBotList import register_chess_bot
from Bots.PiecesMoves import get_all_moves, get_piece_value

INF = 10**3


def chess_bot(player_sequence, board, time_budget, **kwargs):
    color = player_sequence[1]

    safety_time = 0.01
    deadline = time.perf_counter() + max(0, time_budget - safety_time)
    total_node = 0

    def evaluate(curr_board):
        score = 0
        for x in range(curr_board.shape[0]):
            for y in range(curr_board.shape[1]):
                piece = curr_board[x][y]

                if len(piece) == 0:
                    continue

                value = get_piece_value(piece[0])

                score += value if piece[1] == "w" else -value

        return score

    def apply_move(curr_board, move):
        (fx, fy), (tx, ty) = move

        new_board = curr_board.copy()

        piece = new_board[fx][fy]
        if piece[0] == "p" and tx == curr_board.shape[0] - 1:
            new_board[tx][ty] = "q" + piece[1]
        else:
            new_board[tx][ty] = piece
        new_board[fx][fy] = ""

        return new_board

    def time_is_up():
        return time.perf_counter() >= deadline

    class SearchTimeout(Exception):
        pass

    def negamax(curr_board, depth_remaining, alpha, beta, side_to_move):
        nonlocal total_node
        total_node += 1
        if time_is_up():
            raise SearchTimeout()

        sign = 1 if side_to_move == "w" else -1

        if depth_remaining == 0:
            return sign * evaluate(curr_board)

        moves = get_all_moves(curr_board, side_to_move)

        if len(moves) == 0:
            return sign * evaluate(curr_board)

        best_score = -INF

        for m in moves:
            child_board = apply_move(curr_board, m)

            next_side = "b" if side_to_move == "w" else "w"

            score = -negamax(child_board, depth_remaining - 1, -beta, -alpha, next_side)

            if score > best_score:
                best_score = score

            if best_score > alpha:
                alpha = best_score

            if alpha >= beta:
                break

        return best_score

    def find_best_move(curr_board, side_to_move, depth):
        nonlocal total_node
        total_node += 1
        moves = get_all_moves(curr_board, side_to_move)

        if len(moves) == 0:
            for x in range(curr_board.shape[0]):
                for y in range(curr_board.shape[1]):
                    piece = curr_board[x][y]
                    if len(piece) > 0 and piece[1] == side_to_move:
                        return (x, y), (x, y)
            return (0, 0), (0, 0)

        best_move = moves[0]
        best_score = -INF

        alpha = -INF
        beta = INF

        for m in moves:
            if time_is_up():
                raise SearchTimeout()

            child = apply_move(curr_board, m)
            next_side = "b" if side_to_move == "w" else "w"

            score = -negamax(child, depth - 1, -beta, -alpha, next_side)

            if score > best_score:
                best_score = score
                best_move = m

            if score > alpha:
                alpha = score

        return best_move

    best_move = (0, 0), (0, 0)
    depth = 1
    try:
        while True:
            if time_is_up():
                raise SearchTimeout()
            moves = get_all_moves(board, color)

            if len(moves) == 0:
                for x in range(board.shape[0]):
                    for y in range(board.shape[1]):
                        piece = board[x][y]
                        if len(piece) > 0 and piece[1] == color:
                            return (x, y), (x, y)
                return (0, 0), (0, 0)

            best_move = find_best_move(board, color, depth)
            depth += 1
    except SearchTimeout:
        print("Max depth:", depth)
        print("Node visited:", total_node)
        pass

    return best_move[0], best_move[1]


register_chess_bot("NegaMax_ThinkR", chess_bot)
