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
    

if __name__ == "__main__":
    pass