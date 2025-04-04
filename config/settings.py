import os

# settings.py

# Application-specific settings
APP_NAME = 'bili_tetris'
APP_VERSION = '1.0.0'

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logger
'''
CRITICAL = 50
FATAL = CRITICAL
ERROR = 40
WARNING = 30
WARN = WARNING
INFO = 20
DEBUG = 10
NOTSET = 0
'''
LOGGER_LVL = 10

# KBD
KBD_MININTERVAL = 0.05 # unstable when less than 0.03

# Control Panel
CP_ALPHA = 0.7
CP_TOPMOST = True