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

# CV
CV_WINDOW_TITLE = '欢乐俄罗斯方块'
CV_PZONE_BBOX_COLOR = [56, 50, 128] # 主要游玩区域的边框颜色是803238，转化为的BGR
CV_PZONE_BACKGROUND_COLOR = [66, 59, 74] # 主要游玩区域的背景颜色是4A3B42，转化为的BGR
CV_NZONE_COLOR = [65, 58, 73] # 下一个块的背景色493A41

CV_BLOCKS_GHOST_HSV_V_THRESHOLD = 120 # 低于这个亮度的认为是空白，有效消除ghost block
CV_BLOCK_I_COLOR = [148, 254, 25] # 19FE94
CV_BLOCK_J_COLOR = [253, 135, 45] # 2D87FD
CV_BLOCK_L_COLOR = [68, 230, 155] # 9BE644
CV_BLOCK_O_COLOR = [56, 56, 240] # F03838
CV_BLOCK_S_COLOR = [246, 89, 195] # C359F6
CV_BLOCK_T_COLOR = [48, 213, 254] # FED530
CV_BLOCK_Z_COLOR = [67, 134, 249] # F98643