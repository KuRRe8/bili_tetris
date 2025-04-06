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
import numpy as np

class GameConcept():
    '''
    most of the method will be implemented as classmethod.
    '''
    def __init__(self):
        raise RuntimeError('cannot be instantiated')

    @classonlymethod
    def is_collide(cls, board: np.ndarray, block_matrix: np.ndarray, x: int, y: int) -> bool:
        """
        判断当前 block_matrix 放在 (x, y) 是否与 board 碰撞。
        """
        rows, cols = board.shape
        for dy in range(4):
            for dx in range(4):
                if block_matrix[dy][dx] == 0:
                    continue
                by, bx = y + dy, x + dx
                if by < 0 or by >= rows or bx < 0 or bx >= cols:
                    return True
                if board[by][bx] != 0:
                    return True
        return False