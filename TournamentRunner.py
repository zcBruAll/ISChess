from typing import Dict, Sequence, Tuple, List
import sys
import importlib
import os
import numpy as np
from dataclasses import dataclass

from Bots import __all__ as BOT_MODULES
from Bots.ChessBotList import CHESS_BOT_LIST
from ChessRules import move_is_valid, check_player_defeated

def load_all_bots() -> None:
    """Import every bot module so their registration hooks execute."""

    for module_name in BOT_MODULES:
        if module_name in ("__init__", "ChessBotList"):
            continue
        importlib.import_module(f"Bots.{module_name}")


@dataclass
class BoardPiece:
    piece_type: str
    color: str

    def __post_init__(self) -> None:
        self.piece_type = self.piece_type.lower()
        self.color = self.color.lower()

    @property
    def type(self) -> str:
        return self.piece_type

    def string(self) -> str:
        return f"{self.piece_type}{self.color}"

    def __getitem__(self, idx):
        if isinstance(idx, slice):
            return self.string()[idx.start : idx.stop : idx.step]
        return self.string()[idx]

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.string() == other
        return super().__eq__(other)

    def __ne__(self, other) -> bool:
        if isinstance(other, str):
            return self.string() != other
        return super().__ne__(other)

    def __len__(self) -> int:
        return len(self.string())

    def __repr__(self) -> str:
        return f"BoardPiece({self.string()})"


def invert_seq(seq: str) -> str:
    return seq[3:] + seq[:3]

def rot90_coord(size: Tuple[int, int], pt: Tuple[int, int], rot: int) -> Tuple[int, int]:
    rot %= 4

    if rot == 0:
        return pt
    
    y, x = pt
    y2 = size[0] - y - 1
    x2 = size[1] - x - 1

    # 90deg clockwise
    if rot == 1:
        return x, y2

    # 180deg
    if rot == 2:
        return y2, x2

    # 270deg clockwise
    if rot == 3:
        return x2, y

    return

def promote(board: np.ndarray, end: Tuple[int, int], piece: BoardPiece):
    # Only pawns can be promoted
    if piece[0] != "p":
        return

    # Promote to queen only if pawn on last line
    last_row = board.shape[0] - 1
    if end[0] == last_row:
        board[end[0], end[1]] = BoardPiece("q", piece[1])

def apply_move(
    board: np.ndarray,
    move: Tuple[Tuple[int, int], Tuple[int, int]],
    rotation: int
):
    # Convert player coordinates to board coordinates
    start = rot90_coord(board.shape, move[0], rotation)
    end = rot90_coord(board.shape, move[1], rotation)

    # Move the piece
    piece = board[start[0], start[1]]
    board[end[0], end[1]] = piece
    board[start[0], start[1]] = ""

    # Promote pawn if needed
    rot_board = np.rot90(board, rotation)
    promote(rot_board, move[1], piece)
    board[:, :] = np.rot90(rot_board, -rotation)

def play_match(bots: Sequence[Tuple[str, callable]], max_turns: int, time_budget: int, seq: str, board: np.ndarray, game_index: int) -> int:
    def endMatch(turn, player: int):
        print(f"{game_index:>3}.", "Match finished in", turn, "turns -", "White win" if player == 1 else "Black win" if player == -1 else "Draw")
        return player

    for turn in range(max_turns):
        player = turn % 2
        player_seq = invert_seq(seq) if player == 1 else seq

        color = player_seq[1]
        rotation = int(player_seq[2])
        player_board = np.rot90(board, rotation)

        bot_name, bot_function = bots[player]

        try:
            proposed_move = bot_function(
                player_seq, np.copy(player_board), time_budget
            )
        except Exception as exc:
            # Any exception counts as a forfeit
            print(f"Bot '{bot_name}' crashed: {exc}")
            return endMatch(turn + 1, (-1) ** (player + 1))

        if not (
            isinstance(proposed_move, tuple) and
            len(proposed_move) == 2 and
            all(isinstance(p, tuple) and len(p) == 2 for p in proposed_move)
        ):
            # Any invalid move format counts as a forfeit 
            print(f"Bot '{bot_name}' produced an invalid move format: {proposed_move}")
            return endMatch(turn + 1, (-1) ** (player + 1))
        
        if not move_is_valid(player_seq, proposed_move, player_board):
            print(f"Bot '{bot_name}' played an illegal move: {proposed_move}")
            return endMatch(turn + 1, (-1) ** (player + 1))

        apply_move(board, proposed_move, rotation)

        # Opponent got defeated
        if check_player_defeated("w" if color == "b" else "b", player_board):
            return endMatch(turn + 1, (-1) ** player)

    return 0

def initBoard() -> Tuple[str, np.ndarray]:
    print(os.name)
    with open("Data/maps/default.brd", "r", encoding="utf-8") as board_file:
        lines = [line.strip() for line in board_file.readlines() if line.strip()]
    
    player_seq = lines[0]
    rows: List[List[object]] = []
    for line in lines[1:]:
        row: List[object] = []
        for p in line.replace("--", "").split(","):
            row.append(BoardPiece(p[0], p[1]) if p != "" else "")
        rows.append(row)

    return (player_seq, np.array(rows, dtype=object))

def run_tournament(budget: int, max_turns: int, time_budget: int, nb_matches: int) -> Dict[str, Dict[str, Dict[str, int]]]:
    result = {}

    player_seq, board = initBoard()

    def play_game(first, second, nb_match):
        name_first = "White " + first
        name_second = "Black " + second

        if name_first in result:
            if name_second not in result[name_first]:
                result[name_first][name_second] = {"w": 0, "l": 0, "e": 0}
        else:
            result[name_first] = {name_second: {"w": 0, "l": 0, "e": 0}}
        
        for i in range(nb_match):
            game_board = np.copy(board)
            winner = play_match([(name_first, CHESS_BOT_LIST[first]), (name_second, CHESS_BOT_LIST[second])], max_turns, time_budget, player_seq, game_board, i+1)
        
            if winner == 1:
                result[name_first][name_second]["w"] += 1
            elif winner == -1:
                result[name_first][name_second]["l"] += 1
            else:
                result[name_first][name_second]["e"] += 1

    for bot1 in CHESS_BOT_LIST:
        if bot1 == "ManualMover":
            continue
        for bot2 in CHESS_BOT_LIST:
            if bot2 == "ManualMover":
                continue

            if bot1 != bot2:
                n = nb_matches // 2
                play_game(bot1, bot2, n)
                play_game(bot2, bot1, n)
            else:
                play_game(bot1, bot2, nb_matches)

    return result

def print_results(results: Dict[str, Dict[str, Dict[str, int]]]) -> None:
    for bot, matches in results.items():
        for opp, record in matches.items():
            print(f"{bot:<20} vs. {opp:<20} | {record['w']:>3} {record['l']:>3} {record['e']:>3}")

if __name__ == "__main__":
    time_budget = 1
    max_turns = 99
    nb_matches = 10

    load_all_bots()

    print_results(run_tournament(time_budget, max_turns, time_budget, nb_matches))

    sys.exit(0)
