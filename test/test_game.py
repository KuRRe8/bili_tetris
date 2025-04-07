import unittest
import numpy as np
from _utils import Tetrominoes, TetrisBlockType
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
        self.assertTrue(GameConcept.is_collide(board, block, 0, 3))

    def test_right_boundary_collision(self):
        board = np.zeros((20, 10), dtype=int)
        block = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ])
        self.assertTrue(GameConcept.is_collide(board, block, 0, 9))  # 越界

    def test_bottom_boundary_collision(self):
        board = np.zeros((20, 10), dtype=int)
        block = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ])
        self.assertTrue(GameConcept.is_collide(board, block, 18, 3))  # 越界

    def test_no_lines_to_clear(self):
        board = np.zeros((20, 10), dtype=int)
        board[18][0] = 1
        board[19][5] = 1
        new_board, cleared = GameConcept.clear_lines(board)
        self.assertEqual(cleared, 0)
        np.testing.assert_array_equal(new_board, board)

    def test_one_line_clear(self):
        board = np.zeros((20, 10), dtype=int)
        board[19][:] = 1  # bottom full
        board[18][3] = 1  # some noise above
        expected = np.zeros((20, 10), dtype=int)
        expected[19][3] = 1
        new_board, cleared = GameConcept.clear_lines(board)
        self.assertEqual(cleared, 1)
        np.testing.assert_array_equal(new_board, expected)

    def test_multiple_lines_clear(self):
        board = np.zeros((20, 10), dtype=int)
        board[17][:] = 1
        board[18][0] = 1  # partial
        board[19][:] = 1
        expected = np.zeros((20, 10), dtype=int)
        expected[19][0] = 1
        new_board, cleared = GameConcept.clear_lines(board)
        self.assertEqual(cleared, 2)
        np.testing.assert_array_equal(new_board, expected)

    def test_all_lines_clear(self):
        board = np.ones((20, 10), dtype=int)
        new_board, cleared = GameConcept.clear_lines(board)
        self.assertEqual(cleared, 20)
        np.testing.assert_array_equal(new_board, np.zeros((20, 10), dtype=int))


    # after is place block test

    def test_place_simple_block_center(self):
        board = np.zeros((20, 10), dtype=int)
        block = np.array([
            [0, 1, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ])
        result = GameConcept.place_block(board, block, 3, 0)

        self.assertEqual(result[0][4], 1)
        self.assertEqual(result[1][3], 1)
        self.assertEqual(result[1][4], 1)
        self.assertEqual(result[1][5], 1)

    def test_place_over_existing_data(self):
        board = np.zeros((20, 10), dtype=int)
        board[1][4] = 7  # 原始数据
        block = np.array([
            [0, 1, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
        ])
        result = GameConcept.place_block(board, block, 3, 0)
        self.assertEqual(result[1][4], 1)  # 被 block 覆盖

    def test_place_block_out_of_bounds_raises(self):
        board = np.zeros((20, 10), dtype=int)
        block = np.array([
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0],
        ])
        with self.assertRaises(ValueError):
            GameConcept.place_block(board, block, 9, 18)  # 会越右下边界




    def test_vertical_I_block_offset(self):
        # 创建空棋盘
        board = np.zeros((20, 10), dtype=int)

        # 手动构造一个竖着的 I 块（在 Tetrominoes 中应为 spin 1 或 spin 0）
        # 此处我们使用 Tetrominoes 的正式数据
        block_type = TetrisBlockType.I
        shapes = Tetrominoes.shapes[block_type]
        found_vertical = False

        for spin_index, shape in enumerate(shapes):
            shape_array = np.array(shape)
            # 查找竖着的那个版本
            if np.sum(shape_array[:, 1]) == 4:  # 纵向居中
                found_vertical = True
                results = GameConcept.possible_moves(board, block_type)
                xs = [x for spin, x, y in results if spin == spin_index]
                self.assertEqual(len(xs), 10, "竖向 I 块未覆盖全部列")

                break

        self.assertTrue(found_vertical, "未找到竖直 I 块形态")


if __name__ == '__main__':
    unittest.main()
