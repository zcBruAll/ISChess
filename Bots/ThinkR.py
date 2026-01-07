# player_sequence = 0w01b2
import numpy as np
import time
from numpy.lib import _array_utils_impl
from Bots.ChessBotList import register_chess_bot
from typing import Sequence, Tuple

pawn_moves = [
    (1, 0),
]

pawn_eat_moves = [
    (1, -1),
    (1, 1),
]

rook_moves = [
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
]

knight_moves = [
    (2, -1),
    (2, 1),
    (-2, -1),
    (-2, 1),
    (-1, -2),
    (-1, 2),
    (1, -2),
    (1, 2),
]

bishop_moves = [
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
]

queen_moves = [
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
]

king_moves = [
    (0, -1),
    (0, 1),
    (-1, 0),
    (1, 0),
    (1, 1),
    (1, -1),
    (-1, 1),
    (-1, -1),
]

pieces_moves = {
    "p": pawn_moves,
    "q": queen_moves,
    "k": king_moves,
    "b": bishop_moves,
    "n": knight_moves,
    "r": rook_moves,
}

can_move_k_cases = ["q", "b", "r"]


def get_piece_value(piece: str) -> int:
    match piece:
        case "p":
            return 1
        case "n":
            return 4
        case "b":
            return 3
        case "r":
            return 5
        case "q":
            return 9
        case "k":
            return 10
        case _:
            return 0


def get_all_moves(board, side_color) -> Sequence[Sequence[int]]:
    eat_moves = []
    upgrade_moves = []
    normal_moves = []

    def get_pieces_moves(position: Tuple[int, int], board):
        nonlocal eat_moves
        nonlocal upgrade_moves
        nonlocal normal_moves

        # Retrieve the piece to find moves
        piece = board[position[0]][position[1]]
        piece_type = piece[0]
        color = piece[1]

        # Get directions for the piece
        dirs = pieces_moves[piece_type]
        # Maximum distance the piece can travel
        max_dist = 1 if piece_type not in can_move_k_cases else board.shape[0] - 1

        for direction in dirs:
            for i in range(1, max_dist + 1):
                # Compute new positions
                nx = i * direction[0] + position[0]
                ny = i * direction[1] + position[1]

                # If out of board, skip move
                if nx < 0 or nx >= board.shape[0] or ny < 0 or ny >= board.shape[1]:
                    break

                # Retrieve content on the case at new position
                case_content = board[nx][ny]

                # if case is empty, can move onto the case
                if len(case_content) == 0:
                    if piece_type != "p":
                        normal_moves.append(((position[0], position[1]), (nx, ny)))
                    elif nx == board.shape[0] - 1:
                        upgrade_moves.append(((position[0], position[1]), (nx, ny)))
                    else:
                        normal_moves.append(((position[0], position[1]), (nx, ny)))

                    continue

                if case_content[1] == color:
                    break

                # If case contains a piece of same color, can't move onto the case
                if case_content[1] != color and piece_type != "p":
                    eat_moves.append(
                        (
                            ((position[0], position[1]), (nx, ny)),
                            get_piece_value(case_content[0]),
                        )
                    )
                    break

        # If the piece to move is a pawn, can eat in specific conditions
        if piece_type == "p":
            directions = pawn_eat_moves
            for dirs in directions:
                # Compute new positions
                nx = dirs[0] + position[0]
                ny = dirs[1] + position[1]

                # If out of board, skip move
                if nx < 0 or nx >= board.shape[0] or ny < 0 or ny >= board.shape[1]:
                    continue

                # Retrieve content on the case at new position
                case_content = board[nx][ny]

                # if case is empty, can't move onto the case
                if len(case_content) == 0:
                    continue

                # If case contains a piece of same color, can't move onto the case
                if case_content[1] != color:
                    if nx < board.shape[0] - 1:
                        eat_moves.append(
                            (
                                ((position[0], position[1]), (nx, ny)),
                                get_piece_value(case_content[0]),
                            )
                        )
                    else:
                        upgrade_moves.append(((position[0], position[1]), (nx, ny)))

    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            try:
                if len(board[x][y]) <= 0 or board[x][y][1] != side_color:
                    continue
            except Exception:
                print(board, x, y, board[x][y])
            get_pieces_moves((x, y), board)

    eat_moves.sort(key=lambda m: m[1], reverse=True)
    moves = upgrade_moves + [m[0] for m in eat_moves] + normal_moves
    return moves


def is_king_safe(board, color):
    # Find king position
    king_pos = None
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            if board[x][y] == "k" + color:
                king_pos = (x, y)
                break
        if king_pos:
            break

    if not king_pos:
        return False

    # Check if any enemy piece can attack the king
    enemy_color = "b" if color == "w" else "w"
    enemy_moves = get_all_moves(board, enemy_color)

    for move in enemy_moves:
        if move[1] == king_pos:
            return False

    return True


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


def get_legal_moves(board, color):
    moves = get_all_moves(board, color)
    legal = []
    for move in moves:
        test_board = apply_move(board, move)
        if is_king_safe(test_board, color):
            legal.append(move)
    return legal


INF = 10**9


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

        moves = get_legal_moves(curr_board, side_to_move)

        if not moves:
            if not is_king_safe(curr_board, side_to_move):
                return -INF
            return 0

        best_score = -INF

        for m in moves:
            child_board = np.rot90(apply_move(curr_board, m), 2)
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
        moves = get_legal_moves(curr_board, side_to_move)

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

        score = -10000

        for m in moves:
            if time_is_up():
                raise SearchTimeout()

            child = np.rot90(apply_move(curr_board, m), 2)

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


register_chess_bot("ThinkR", chess_bot)
