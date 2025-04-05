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

class TetrisBlockType(Enum):
    I = "I"
    O = "O"
    T = "T"
    S = "S"
    Z = "Z"
    J = "J"
    L = "L"

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