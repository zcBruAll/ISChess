from numpy.random.mtrand import Sequence

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

def get_pieces_moves(position: (int, int), board) -> Sequence[int, int]:
    # Retrieve the piece to find moves
    piece = board[position[0]][position[1]]
    piece_type = piece[0]
    color = piece[1]

    # Get directions for the piece
    dirs = pieces_moves[piece_type]
    # Maximum distance the piece can travel
    max_dist = 1 if piece_type not in can_move_k_cases else board.shape[0] - 1

    moves = []
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
                moves.append((nx, ny))
                continue

            if case_content[1] == color:
                break

            # If case contains a piece of same color, can't move onto the case
            if case_content[1] != color and piece_type != "p":
                moves.append((nx, ny))
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
                moves.append((nx, ny))

    return moves