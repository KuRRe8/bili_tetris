"""
File: game.py
Author: KuRRe8
Created: 2025-04-06
Description:
    用于创建一个数字孪生,XD。 已经在utils定义了基本的方块类型和形态,在alg中定义了当前游戏场景状态GameState
    本文件实现游戏的基本规则，用于判断操作是否合法，作为评估价值函数之前的检测。
    由于是模拟桃谷游戏的欢乐俄罗斯方块，规则相对简单
    本次实现，只考虑如下内容：
        碰撞检测
        行数消除
        攻击分数（多行消除优于单行）， 在这个块中，消除1行会给对面加1碎块，2行给对面加2碎块，3行给对面加1行碎块，4行给对面加2行碎块
            在双方都是高手的情况下，3消4消不一定是最优解，反而碎块会给对方造成干扰，但为了简洁起见，会大力增加3消4消的权重
            本文件只反馈实际分数，比如1消得到1+0.1分，2消除得到2+0.4分，3消得到3+0.8分，4消得到4+1.6分
                                2一消2.2，3一消3.3  ，4一消4.4
                                         1.5二消3.6 ，2二消4.8
                                                   1.33三消5.05
                                                   1四消5.6
            而堆叠高度和空洞数量等加权考量只放在alg.py中，不在游戏仿真中设置。alg用于评估地形，game用于反馈当前步骤得分，更新下一个地形
"""

import config.settings
from _logger import logger
from _utils import classonlymethod
from _utils import Tetrominoes, TetrisBlockType

import numpy as np
from typing import Tuple, Dict, List, Optional, Union, Any

class GameConcept():
    '''
    most of the method will be implemented as classmethod.
    '''
    def __init__(self):
        raise RuntimeError('cannot be instantiated')

    
    @classonlymethod
    def is_collide(cls, board: np.ndarray, block_matrix: np.ndarray, row_now: int, col_now: int) -> bool:

        rows, cols = board.shape
        for row_idx in range(4):
            for col_idx in range(4):
                if block_matrix[row_idx][col_idx] == 0:
                    continue
                board_row_idx, board_col_idx = row_now+row_idx, col_now+col_idx
                if board_col_idx < 0 or board_col_idx >= cols or board_row_idx < 0 or board_row_idx >= rows:
                    return True
                if board[board_row_idx][board_col_idx] != 0:
                    return True
        return False
    

    @classonlymethod
    def clear_lines(cls, board: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        对当前棋盘执行行消除，返回新棋盘和消除行数。
        满一整行（非零）就消除，并将上面的行下移。
        """
        new_board = board[~np.all(board == 1, axis=1)]
        cleared = board.shape[0] - new_board.shape[0]
        new_board = np.vstack([np.zeros((cleared, board.shape[1]), dtype=int), new_board])
        return new_board, cleared

    @classonlymethod
    def clear_lines_attack_score(cls, cleared: int) -> float:
        fac = 2
        match cleared:
            case 0:
                return 0.1*fac
            case 1:
                return 1.1*fac
            case 2:
                return 2.4*fac
            case 3:
                return 3.8*fac
            case 4:
                return 5.6*fac
            case _: # may get more than 4 clear because of garbage block
                return 5.6*fac
    
    @classonlymethod
    def place_block(cls, board: np.ndarray, block_matrix: np.ndarray, column_offest: int, row_offset: int) -> np.ndarray:
        """
        将 block_matrix 放置到 board 的 (x, y)，返回新的 board（不修改原始）。
        """
        new_board = board.copy()
        rows, cols = board.shape

        for block_row_idx in range(4):
            for block_column_index in range(4):
                if block_matrix[block_row_idx][block_column_index] == 0:
                    continue
                board_row_idx, board_column_index = row_offset + block_row_idx, column_offest + block_column_index
                if 0 <= board_row_idx < rows and 0 <= board_column_index < cols:
                    new_board[board_row_idx][board_column_index] = block_matrix[block_row_idx][block_column_index]
                else:
                    raise ValueError(f"Block out of bounds at ({board_column_index}, {board_row_idx} in Cartesian)")
        return new_board
    
    @classonlymethod
    def get_final_row_pos_giving_col(cls, board: np.ndarray, block_matrix: np.ndarray, col_offset: int, row_offset_start: int = 2) -> int:
        """
        模拟 block 从 start_y 开始向下自由落体，返回最后能放置的 y 值（不碰撞）。
        注意：不会修改原始棋盘，也不会进行放置。

        这里行索引从2开始， 默认不考虑在堆叠极高情况的计算
        """
        row_offset = row_offset_start
        while not GameConcept.is_collide(board, block_matrix, row_offset, col_offset):
            row_offset += 1
        return row_offset - 1

    @classonlymethod
    def possible_moves(cls, board: np.ndarray, block_type: TetrisBlockType) -> List[Tuple[int, int, int]]:
        """
        给定当前棋盘和一个 block 类型，返回所有合法放置位置：
        """
        rows, cols = board.shape
        results = []

        shapes = Tetrominoes.shapes[block_type]
        for spin_index, shape in enumerate(shapes):
            block_matrix = np.array(shape)

            used_cells = [(row_idx, col_idx) for row_idx in range(4) for col_idx in range(4) if block_matrix[row_idx][col_idx]]
            if not used_cells:
                continue

            min_col_idx = min(__ for _, __ in used_cells)
            max_col_idx = max(__ for _, __ in used_cells)
            block_width = max_col_idx - min_col_idx + 1

            for col_idx in range(cols - block_width + 1):
                actual_col_now = col_idx - min_col_idx  # 对齐左边边界
                try:
                    lowest_row_idx_now = GameConcept.get_final_row_pos_giving_col(board, block_matrix, actual_col_now)
                    if not GameConcept.is_collide(board, block_matrix, lowest_row_idx_now, actual_col_now):
                        results.append((spin_index, lowest_row_idx_now, actual_col_now))
                except ValueError:
                    continue

        return results