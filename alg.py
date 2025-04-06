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

    def __repr__(self):
        return (f"GameState(Board shape={self.game_board.shape}, "
                f"current_block={self.current_block}, next_block={self.next_block})")
    
class SearchAlgorithm:
    @_utils.classonlymethod
    def _evaluate(cls, current_attack: float = 0.0) -> int:
        state = GameState()
        board = state.game_board
        rows, cols = board.shape

        score = 0
        min_y = np.zeros(cols + 1, dtype=int) # one more column for height check

        # Unified evaluation weights
        factor = {'hole': -50, 'h_change': -5, 'y_factor': -10, 'h_variance': -10}

        # Column heights (min_y)
        for x in range(cols):
            for y in range(rows):
                if board[y, x] != 0:
                    min_y[x] = y
                    break
            else:
                min_y[x] = rows

        # Hole count
        hole_score = 0
        for x in range(cols):
            for y in range(min_y[x] + 1, rows):
                if board[y, x] == 0:
                    hole_score += factor['hole']
        score += hole_score

        # Height change
        for x in range(1, cols):
            v = min_y[x] - min_y[x - 1]
            score += abs(v) * factor['h_change']

        # Refined average height: exclude 1~2 outliers
        sorted_heights = np.sort(min_y[:cols])
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
        h_var_sum = sum((avg_height - min_y[x]) ** 2 for x in range(cols))
        h_variance_score = h_var_sum * factor['h_variance'] / (cols * 100)
        score += int(h_variance_score)

        # Add attack score from game module
        score += int(current_attack)

        return int(score)
    
    @_utils.classonlymethod
    def _get_attack_result(cls):
        """
        Calculate the attack result based on the current game state.
        :param
        :return: 
        """
        pass
    
    @_utils.classonlymethod
    def search(self) :
        """
        Perform a search algorithm to find the best move.
        :param 
        :return: 
        """
        pass

if __name__ == "__main__":
    pass