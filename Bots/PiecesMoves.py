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
            return 3
        case "b":
            return 3
        case "r":
            return 5
        case "q":
            return 9
        case "k":
            return 10000
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
            for direction in pawn_eat_moves:
                # Compute new positions
                nx = direction[0] + position[0]
                ny = direction[1] + position[1]

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

    eat_moves.sort(key=lambda m: m[1])
    moves = [m[0] for m in eat_moves] + upgrade_moves + normal_moves
    return moves
