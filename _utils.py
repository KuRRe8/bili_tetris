"""
File: _utils.py
Author: KuRRe8
Created: 2025-04-05
Description:
    
"""

import config.settings
from _logger import logger
from enum import Enum
from typing import List, Tuple
import pygetwindow as gw

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
            logger.debug(f"Set focus to window with handle: {window._hWnd}")
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