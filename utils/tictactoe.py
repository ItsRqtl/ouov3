"""
Tic Tac Toe Minimax Algorithm evaluation function

This file is part of ouoteam/ouov3 which is released under GNU General Public License v3.0.
See file LISENCE for full license details.
"""

from __future__ import annotations

import itertools

import numpy as np

__all__ = ["Tictactoe"]


class Tictactoe:
    """
    This class represents a Tic Tac Toe game.
    """

    def __init__(self):
        self.board = np.array([["", "", ""], ["", "", ""], ["", "", ""]])

    def move(self, row: int, col: int, player: str) -> str | bool | None:
        """
        This function makes a move on the board.

        :param row: The row index of the move.
        :type row: int
        :param col: The column index of the move.
        :type col: int
        :param player: The player making the move.
        :type player: str

        :raises ValueError: If the move is invalid.
        :raises ValueError: If the player is invalid.

        :return: X if X won, O if O won, None if the game is tied, and False if the game is not over.
        :rtype: Optional[Union[str, bool]]
        """
        if player not in ["X", "O"]:
            raise ValueError("Invalid player.")
        if row < 0 or row > 2 or col < 0 or col > 2 or self.board[row][col] != "":
            raise ValueError("Invalid move.")
        self.board[row][col] = player
        return self.evaluate_result()

    def evaluate_result(self) -> str | bool | None:
        """
        This function checks if the game is over.

        :return: X if X won, O if O won, None if the game is tied, and False if the game is not over.
        :rtype: Optional[Union[str, bool]]
        """
        # check rows
        for row in self.board:
            if all(cell == "X" for cell in row):
                return "X"
            elif all(cell == "O" for cell in row):
                return "O"

        # check columns
        for col in range(3):
            if all(self.board[row][col] == "X" for row in range(3)):
                return "X"
            elif all(self.board[row][col] == "O" for row in range(3)):
                return "O"

        # check diagonals
        if all(self.board[i][i] == "X" for i in range(3)):
            return "X"
        elif all(self.board[i][i] == "O" for i in range(3)):
            return "O"

        # check other diagonal
        if all(self.board[i][2 - i] == "X" for i in range(3)):
            return "X"
        elif all(self.board[i][2 - i] == "O" for i in range(3)):
            return "O"

        # check if the game is tied or not over yet
        return None if np.all(self.board != "") else False

    def get_score(self) -> int:
        """
        This function evaluates the current state of the board and returns a score based on
        how favorable the board is for the computer player (X). A positive score means X is winning,
        a negative score means O is winning, and a score of zero means the game is tied.

        :return: The score of the current board state.
        :rtype: int
        """
        for row in self.board:
            if all(cell == "X" for cell in row):
                return 10
            elif all(cell == "O" for cell in row):
                return -10

        for col in range(3):
            if all(self.board[row][col] == "X" for row in range(3)):
                return 10
            elif all(self.board[row][col] == "O" for row in range(3)):
                return -10

        if all(self.board[i][i] == "X" for i in range(3)):
            return 10
        elif all(self.board[i][i] == "O" for i in range(3)):
            return -10

        if all(self.board[i][2 - i] == "X" for i in range(3)):
            return 10
        elif all(self.board[i][2 - i] == "O" for i in range(3)):
            return -10
        return 0

    def minimax(self, depth: int, is_maximizing: bool) -> int:
        """
        This function uses the minimax algorithm to evaluate the best next move for the computer player (X).

        :param depth: The depth of the tree.
        :type depth: int
        :param is_maximizing: Whether or not the current player is maximizing.
        :type is_maximizing: bool

        :return: The score of the current board state.
        :rtype: int
        """
        score = self.get_score()
        if score in [10, -10]:
            return score - depth
        if np.all(self.board != ""):
            return 0
        if is_maximizing:
            best_score = -np.inf
            for i, j in itertools.product(range(3), range(3)):
                if self.board[i][j] == "":
                    self.board[i][j] = "X"
                    score = self.minimax(depth + 1, False)
                    self.board[i][j] = ""
                    best_score = max(score, best_score)
        else:
            best_score = np.inf
            for i, j in itertools.product(range(3), range(3)):
                if self.board[i][j] == "":
                    self.board[i][j] = "O"
                    score = self.minimax(depth + 1, True)
                    self.board[i][j] = ""
                    best_score = min(score, best_score)
        return best_score

    def get_best_move(self) -> tuple[int, int]:
        """
        This function uses the minimax algorithm to evaluate the best next move for the computer player (X),
        and returns the row and column indices of the best move.

        :return: The row and column indices of the best move.
        :rtype: tuple[int, int]
        """
        best_score = -np.inf
        best_move = None
        for i, j in itertools.product(range(3), range(3)):
            if self.board[i][j] == "":
                self.board[i][j] = "X"
                score = self.minimax(0, False)
                self.board[i][j] = ""
                if score > best_score:
                    best_score = score
                    best_move = (i, j)
        return best_move
