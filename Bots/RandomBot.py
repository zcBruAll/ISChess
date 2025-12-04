# player_sequence = 0w01b2
import random
from Bots.ChessBotList import register_chess_bot
from Bots.PiecesMoves import get_pieces_moves

def chess_bot(player_sequence, board, time_budget, **kwargs):
    color = player_sequence[1]
    pieces = []
    # Retrieve every piece position of our color on the board
    for x in range(board.shape[0]):
        for y in range(board.shape[1]):
            piece = board[x][y]
            if len(piece) > 0 and piece[1] == color:
                pieces.append((x, y))

    # Select a random piece to move
    random_piece = random.choice(pieces)

    # Retrieve all possibles moves for selected piece
    moves = get_pieces_moves((random_piece[0], random_piece[1]), board)

    # By default, don't move
    move = random_piece
    # if at least 1 possible move exists, choose randomly one
    if len(moves) > 0:
        move = random.choice(moves)

    # Return the selected move
    return random_piece, move

# Register the bot to bot list
register_chess_bot("RandomBot", chess_bot)