"""
File: _utils.py
Author: KuRRe8
Created: 2025-04-05
Description:
    
"""

import config.settings
from _logger import logger
from enum import Enum
from typing import List, Tuple, Dict, Union, Optional
import pygetwindow as gw
import numpy as np

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]
    

class classonlymethod(classmethod):
    """
    decorator for class methods that should only be called on the class, not on instances.
    """
    def __get__(self, instance, cls=None):
        if instance is not None:
            raise AttributeError("This method is available only on the class, not on instances.")
        return super(classonlymethod, self).__get__(instance, cls)
    
class WindowUtils:
    @classonlymethod
    def find_tetris_window(cls) -> gw.Window:
        """
        Find the Tetris window based on the title.
        """
        windows = gw.getWindowsWithTitle(config.settings.CV_WINDOW_TITLE)
        if not windows:
            raise RuntimeError(f"Window '{config.settings.CV_WINDOW_TITLE}' not found.")
        return windows[0]  # Win32window type, get the first one, since if try to find a window solely by name may reture multiple windows.

    @classonlymethod
    def bring_to_front(cls, window: gw.Window) -> None:
        """
        Bring the Tetris window to the front.
        """
        if not isinstance(window, gw.Window):
            raise TypeError("Expected a pygetwindow.Window instance.")
        try:
            import win32gui
            win32gui.SetForegroundWindow(window._hWnd)  # Bring the window to the foreground
        except ImportError:
            logger.error("win32gui module is not available. Cannot set focus to window.")
            return
        
class TetrisBlockType(Enum):
    I = "I"
    O = "O"
    T = "T"
    S = "S"
    Z = "Z"
    J = "J"
    L = "L"

class Tetrominoes:
    '''
    This class define the shape of each Tetrominoe in each spin
    One efficient representation is bitmap, but I will use direct representation in a 4*4 grid.
    '''

    # class variables
    shapes = {
        TetrisBlockType.I: [
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 1, 1],
                [0, 0, 0, 0],
            ],
            [
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
            ],
        ],
        TetrisBlockType.O: [
            [
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
            ],
        ],
        TetrisBlockType.T: [
            [
                [0, 0, 0, 0],
                [0, 1, 0, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 1, 0],
                [0, 1, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 1, 0, 0],
                [1, 1, 0, 0],
                [0, 1, 0, 0],
            ],
        ],
        TetrisBlockType.S: [
            [
                [0, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [1, 1, 0, 0],
                [0, 0, 0, 0],
            ],
        ],
        TetrisBlockType.Z: [
            [
                [0, 0, 1, 0],
                [0, 1, 1, 0],
                [0, 1, 0, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [0, 1, 1, 0],
                [0, 0, 0, 0],
            ],
        ],
        TetrisBlockType.J: [
            [
                [0, 0, 0, 0],
                [1, 0, 0, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 1, 1, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 1, 0],
                [0, 0, 1, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [1, 1, 0, 0],
            ],
        ],
        TetrisBlockType.L: [
            [
                [0, 0, 0, 0],
                [0, 0, 1, 0],
                [1, 1, 1, 0],
                [0, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 1, 0],
            ],
            [
                [0, 0, 0, 0],
                [0, 0, 0, 0],
                [1, 1, 1, 0],
                [1, 0, 0, 0],
            ],
            [
                [0, 0, 0, 0],
                [1, 1, 0, 0],
                [0, 1, 0, 0],
                [0, 1, 0, 0],
            ],
        ],
    }
    
    
    
    Tetris_Col_H: Optional[ dict[ TetrisBlockType, Union[np.ndarray,list[list]] ] ]= {}    
    # for each block type, have ndarray, first dimension is spin, second dimension is 4 columns height that been filled.

    # this variable will build statically at each time this script first imported.
    # typically it looks like this
    '''
        {<TetrisBlockType.T: 'T'>: [[3, 3, 3, 0],
                                    [0, 4, 3, 0],
                                    [3, 4, 3, 0],
                                    [3, 4, 0, 0]],
        <TetrisBlockType.O: 'O'>: [[0, 3, 3, 0]],
        <TetrisBlockType.L: 'L'>: [[3, 3, 3, 0],
                                    [0, 4, 4, 0],
                                    [4, 3, 3, 0],
                                    [2, 4, 0, 0]],
        <TetrisBlockType.I: 'I'>: [[3, 3, 3, 3], [0, 4, 0, 0]],
        <TetrisBlockType.J: 'J'>: [[3, 3, 3, 0],
                                    [0, 4, 2, 0],
                                    [3, 3, 4, 0],
                                    [4, 4, 0, 0]],
        <TetrisBlockType.Z: 'Z'>: [[0, 3, 2, 0], [2, 3, 3, 0]],
        <TetrisBlockType.S: 'S'>: [[0, 2, 3, 0], [3, 3, 2, 0]]}
    '''



    for block_type, rotations in shapes.items():
        Tetris_Col_H[block_type] = []
        for shape in rotations:
            shape_np = np.array(shape)
            col_heights = [0] * 4
            for col_idx in range(4):
                for row_idx in range(4):
                    if shape_np[row_idx][col_idx]:
                        col_heights[col_idx] = row_idx + 1
            Tetris_Col_H[block_type].append(col_heights)

    logger.info('Tetris_Col_H calculated.')