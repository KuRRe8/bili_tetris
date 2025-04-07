"""
File: alg.py
Author: KuRRe8
Created: 2025-04-05
Description:
    Implement BFS alg for searching. In Verison 1 I will utilizing an evaluation function and use traditional machine learning method.
    May develop PPO reinforcement learning in the future.
"""

import config.settings
from _logger import logger
import cv2
import numpy as np
from typing import List, Tuple, Optional, Any
import _utils

class GameState(metaclass=_utils.SingletonMeta):
    """
    singleton
    """
    def __init__(self, rows=20, cols=10):
        logger.info('Singleton instance of GameState created!!!!!')
        # Game Board represented as a 2D numpy array, filled area (FA) and blank area (BA)
        # 0 indicates an empty cell, non-zero values represent filled cells
        self.game_board = np.zeros((rows, cols), dtype=np.int8)
        # Current block (CB): the block currently controlled in the game
        self.current_block: Optional[_utils.TetrisBlockType] = None
        # Next block (NB): the upcoming block preview from the N zone
        self.next_block: Optional[_utils.TetrisBlockType] = None
        self.up_to_date = False

    def update_board(self, board_data: np.ndarray):
        """
        Update the FA (filled area) with new board data.
        :param board_data: A numpy ndarray with shape matching self.game_board.
        """
        if board_data.shape != self.game_board.shape:
            raise ValueError("Board data shape mismatch.")
        self.game_board = board_data.copy()
        logger.debug('Updating game board in GameState Class')

    def update_current_block(self, block):
        logger.debug(f"Updating current block in GameState Class: {block}")

        self.current_block = block

    def update_next_block(self, block):
        logger.debug(f"Updating next block in GameState Class: {block}")
        self.next_block = block

    def reset(self):
        """
        Resets the game state to initial values.
        """
        self.game_board.fill(0)
        self.current_block = None
        self.next_block = None
        self.up_to_date = False

    def __repr__(self):
        return (f"GameState(Board shape={self.game_board.shape}, "
                f"current_block={self.current_block}, next_block={self.next_block})")
    
class SearchAlgorithm:
    @_utils.classonlymethod
    def _evaluate(cls, board: np.ndarray, current_attack: float = 0.0) -> int:

        rows, cols = board.shape

        score = 0
        min_col_height = np.zeros(cols, dtype=int) # large number when there is no block

        # Unified evaluation weights
        factor = {'hole': -80, 'h_change': -5, 'y_factor': -10, 'h_variance': -10}

        # Column heights (min_col_idx)
        for col_idx in range(cols):
            for row_index in range(rows):
                if board[row_index, col_idx] != 0:
                    min_col_height[col_idx] = row_index
                    break
            else:
                min_col_height[col_idx] = rows

        # Hole count
        hole_score = 0
        for col_idx in range(cols):
            for row_index in range(min_col_height[col_idx] + 1, rows):
                if board[row_index, col_idx] == 0:
                    hole_score += factor['hole']
        score += hole_score

        # Height change
        for col_idx in range(1, cols):
            v = min_col_height[col_idx] - min_col_height[col_idx - 1]
            score += abs(v) * factor['h_change']

        # Refined average height: exclude 1~2 outliers
        sorted_heights = np.sort(min_col_height[:cols])
        trimmed_heights = sorted_heights[1:-1] if cols > 2 else sorted_heights
        avg_height = np.mean(trimmed_heights)

        # Apply Y factor penalty only if average height is out of 4~10 range
        if avg_height < 4:
            penalty = (4 - avg_height) ** 2
            score += int(factor['y_factor'] * penalty / rows)
        elif avg_height > 10:
            penalty = (avg_height - 10) ** 2
            score += int(factor['y_factor'] * penalty / rows)

        # Height variance
        h_var_sum = sum((avg_height - min_col_height[col_idx]) ** 2 for col_idx in range(cols))
        h_variance_score = h_var_sum * factor['h_variance'] / (1 * 100) # previously cols * 100
        score += int(h_variance_score)

        # Add attack score from game module
        score += int(current_attack)

        return int(score)
    
    @_utils.classonlymethod
    def _get_attack_result(cls, board: np.ndarray, block_matrix: np.ndarray, row_idx: int, col_idx: int) -> Tuple[np.ndarray, float]:
        """
        放置 block_matrix 到指定位置后，执行行消除，并返回 (新棋盘, 攻击得分)
        """
        from game import GameConcept  # 避免循环引用问题

        new_board = GameConcept.place_block(board, block_matrix, col_idx, row_idx)
        cleared_board, cleared_lines = GameConcept.clear_lines(new_board)
        attack_score = GameConcept.clear_lines_attack_score(cleared_lines)

        return cleared_board, attack_score
    
    @_utils.classonlymethod
    def search(cls) -> Tuple[int, int, int]:
        from game import GameConcept

        state = GameState()
        board_before_decision = state.game_board
        cur_block = state.current_block
        next_block = state.next_block

        assert cur_block is not None, "Current block must be set"
        legal_moves = GameConcept.possible_moves(board_before_decision, cur_block)

        best_score = -float('inf')
        best_move = None

        for spin_idx, row_idx, col_idx in legal_moves:
            block_matrix = np.array(_utils.Tetrominoes.shapes[cur_block][spin_idx])
            board_after, attack_score = cls._get_attack_result(board_before_decision, block_matrix, row_idx, col_idx)

            # depth-1 score
            score = cls._evaluate(board=board_after,current_attack=attack_score)

            # depth-2 search if next block available
            if next_block is not None:
                next_moves = GameConcept.possible_moves(board_after, next_block)
                second_best = -float('inf')
                for next_spin, next_row, next_col in next_moves:
                    next_block_matrix = np.array(_utils.Tetrominoes.shapes[next_block][next_spin])
                    board_after2, attack_score2 = cls._get_attack_result(board_after, next_block_matrix, next_row, next_col)
                    s = cls._evaluate(board=board_after2,current_attack=attack_score2)
                    if s > second_best:
                        second_best = s
                score += second_best

            if score > best_score:
                best_score = score
                best_move = (spin_idx, row_idx, col_idx)

        return best_move







def test_alg_setUp1():
    """
    Set up a GameState instance with a predefined board and blocks.
    """
    state = GameState()
    # Construct a board with the left bottom 10 rows and 9 columns filled
    board = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    ], dtype=np.int8)
    state.update_board(board)

    # Set the current block to I and the next block to T
    state.update_current_block(_utils.TetrisBlockType.I)
    state.update_next_block(_utils.TetrisBlockType.T)

def test_alg_setUp2():
    """
    Set up a GameState instance with a more complex predefined board and blocks.
    """
    state = GameState()
    # Construct a board with a more complex configuration
    board = np.array([
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 0, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
    ], dtype=np.int8)
    state.update_board(board)

    # Set the current block to L and the next block to Z
    state.update_current_block(_utils.TetrisBlockType.T)
    state.update_next_block(_utils.TetrisBlockType.Z)

def test_search():
    """
    Test the search method of SearchAlgorithm with the predefined GameState.
    """
    best_move = SearchAlgorithm.search()
    pass

if __name__ == "__main__":
    test_alg_setUp2()
    test_search()
    pass