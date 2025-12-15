import importlib
import time
import numpy as np
import pytest

from Bots import __all__ as BOT_MODULES
from Bots.ChessBotList import CHESS_BOT_LIST
from ChessRules import move_is_valid, check_player_defeated


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
    assert move_is_valid(player_sequence, move, board), f"Illegal move: {move}"


@pytest.fixture(scope="session", autouse=True)
def _load_bots_once():
    load_all_bots()


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_returns_correct_format_move(bot_name):
    board = np.array([["pw", ""], ["", "pb"]])
    move = run_bot(bot_name, "0w01b2", board, 1)
    assert_move_in_bounds(board, move)


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_returns_legal_move_when_moves_exist(bot_name):
    board = np.array([["pw"], [""], ["pb"]])
    move = run_bot(bot_name, "0w01b2", board, 1)
    assert move == ((0, 0), (1, 0)), f"Move returned: {move}"
    # TODO: Make board an array of ChessPieces to not raise error
    # assert_move_is_valid_for_rules("0w01b2", board, move)


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_returns_current_pos_when_no_move(bot_name):
    board = np.array([[""], ["pw"], ["pb"]])
    move = run_bot(bot_name, "0w01b2", board, 1)
    assert move == ((1, 0), (1, 0)), f"Move returned: {move}"
    # assert_move_is_valid_for_rules("0w01b2", board, move)


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_avoid_loosing_queen(bot_name):
    board = np.array([["qw"], [""], ["pb"], ["rb"]])
    move = run_bot(bot_name, "0w01b2", board, 3)
    assert move != ((0, 0), (2, 0)), f"Queen blundered into rook: {move}"


@pytest.mark.parametrize("bot_name", ["NegaMax_ThinkR"])
def test_bot_respect_time_budget(bot_name):
    board = np.array(
        [
            ["rw", "nw", "bw", "qw"],
            ["pw", "pw", "pw", "pw"],
            ["", "", "", ""],
            ["pb", "pb", "pb", "pb"],
            ["rb", "nb", "bb", "qb"],
        ]
    )

    time_budget = 1
    t0 = time.perf_counter()
    move = run_bot(bot_name, "0w01b2", board, time_budget)
    t1 = time.perf_counter()

    assert (t1 - t0) <= time_budget + 0.05, f"Took too long: {t1 - t0}s, move={move}"
    assert_move_in_bounds(board, move)
