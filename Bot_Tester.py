import importlib
import time
import numpy as np
import pytest
from dataclasses import dataclass

from Bots import __all__ as BOT_MODULES
from Bots.ChessBotList import CHESS_BOT_LIST
from ChessRules import move_is_valid, check_player_defeated


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


def load_all_bots() -> None:
    """Import every bot module so their registration hooks execute."""

    for module_name in BOT_MODULES:
        if module_name in ("__init__", "ChessBotList"):
            continue
        importlib.import_module(f"Bots.{module_name}")


def run_bot(bot_name, player_sequence, board, time_budget):
    bot_func = CHESS_BOT_LIST[bot_name]
    move = bot_func(player_sequence, board, time_budget)
    assert isinstance(move, tuple) and len(move) == 2, f"Bot returned {move}"
    assert isinstance(move[0], tuple) and isinstance(
        move[1], tuple
    ), f"Bot returned {move}"
    assert len(move[0]) == 2 and len(move[1]) == 2, f"Bot returned {move}"
    return move


def assert_move_in_bounds(board, move):
    (fx, fy), (tx, ty) = move
    h, w = board.shape[0], board.shape[1]
    assert 0 <= fx < h and 0 <= fy < w, f"from square out of bounds: {move}"
    assert 0 <= tx < h and 0 <= ty < w, f"to square out of bounds: {move}"


def assert_move_is_valid_for_rules(player_sequence, board, move):
    assert_move_in_bounds(board, move)
    assert move_is_valid(player_sequence, move, board, True), f"Illegal move: {move}"


@pytest.fixture(scope="session", autouse=True)
def _load_bots_once():
    load_all_bots()


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_returns_correct_format_move(bot_name):
    board = np.array(
        [[BoardPiece("p", "w"), ""], ["", BoardPiece("p", "b")]], dtype=object
    )
    move = run_bot(bot_name, "0w01b2", board, 1)
    assert_move_in_bounds(board, move)


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_returns_legal_move_when_moves_exist(bot_name):
    board = np.array(
        [[BoardPiece("p", "w")], [""], [BoardPiece("p", "b")]], dtype=object
    )
    move = run_bot(bot_name, "0w01b2", board, 1)
    assert_move_is_valid_for_rules("0w01b2", board, move)


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_returns_current_pos_when_no_move(bot_name):
    board = np.array(
        [[""], [BoardPiece("p", "w")], [BoardPiece("p", "b")]], dtype=object
    )
    move = run_bot(bot_name, "0w01b2", board, 1)
    assert move == ((1, 0), (1, 0)), f"Invalid move: {move}"


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_avoid_loosing_queen(bot_name):
    board = np.array(
        [[BoardPiece("q", "w")], [""], [BoardPiece("p", "b")], [BoardPiece("r", "b")]],
        dtype=object,
    )
    move = run_bot(bot_name, "0w01b2", board, 3)
    assert move != ((0, 0), (2, 0)), f"Queen blundered into rook: {move}"


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_respect_time_budget(bot_name):
    board = np.array(
        [
            [
                BoardPiece("r", "w"),
                BoardPiece("n", "w"),
                BoardPiece("b", "w"),
                BoardPiece("q", "w"),
            ],
            [
                BoardPiece("p", "w"),
                BoardPiece("p", "w"),
                BoardPiece("p", "w"),
                BoardPiece("p", "w"),
            ],
            ["", "", "", ""],
            [
                BoardPiece("p", "b"),
                BoardPiece("p", "b"),
                BoardPiece("p", "b"),
                BoardPiece("p", "b"),
            ],
            [
                BoardPiece("r", "b"),
                BoardPiece("n", "b"),
                BoardPiece("b", "b"),
                BoardPiece("q", "b"),
            ],
        ],
        dtype=object,
    )

    time_budget = 1
    t0 = time.perf_counter()
    move = run_bot(bot_name, "0w01b2", board, time_budget)
    t1 = time.perf_counter()

    assert (t1 - t0) <= time_budget, f"Took too long: {t1 - t0}s, move={move}"
    assert_move_in_bounds(board, move)


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_know_queen_upgrade(bot_name):
    board = np.array(
        [
            ["", BoardPiece("r", "b"), "", "", ""],
            ["", "", "", "", ""],
            [BoardPiece("p", "w"), BoardPiece("p", "w"), "", "", BoardPiece("p", "b")],
            [BoardPiece("k", "w"), "", "", "", ""],
        ],
        dtype=object,
    )

    move = run_bot(bot_name, "1b20w0", board, 1)
    assert move == ((2, 4), (3, 4)), f"Wrong move: {move}"
