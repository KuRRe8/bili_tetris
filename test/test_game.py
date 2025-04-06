import unittest
import numpy as np
from game import GameConcept

class TestGameConcept(unittest.TestCase):

    def test_no_collision(self):
        board = np.zeros((20, 10), dtype=int)
        block = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ])
        self.assertFalse(GameConcept.is_collide(board, block, 3, 0))

    def test_overlap_with_existing(self):
        board = np.zeros((20, 10), dtype=int)
        board[1][4] = 1  # 与方块正好重叠
        block = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ])
        self.assertTrue(GameConcept.is_collide(board, block, 3, 0))

    def test_right_boundary_collision(self):
        board = np.zeros((20, 10), dtype=int)
        block = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ])
        self.assertTrue(GameConcept.is_collide(board, block, 9, 0))  # 越界

    def test_bottom_boundary_collision(self):
        board = np.zeros((20, 10), dtype=int)
        block = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ])
        self.assertTrue(GameConcept.is_collide(board, block, 3, 18))  # 越界


if __name__ == '__main__':
    unittest.main()
