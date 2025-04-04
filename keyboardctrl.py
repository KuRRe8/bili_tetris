"""
File: keyboardctrl.py
Author: KuRRe8
Created: 2025-04-05
Description:
    控制键盘操作的模块，包括左移、右移、变形，快速下落等功能。
"""

import config.settings
from _logger import logger
import keyboard
import time


class KeyboardController:
    """
    Encapsulated the keyboard control method.
    Rotate before move left right since rotate will change the position near the wall.
    """
    def __init__(self):
        pass

    def press_left(self):
        keyboard.send('left')

    def press_right(self):
        keyboard.send('right')

    def press_drop(self):
        keyboard.send('space')

    def press_rotate(self):
        keyboard.send('e')

    def press_soft_drop(self):
        keyboard.send('down')

    def multi_left(self,multi: int):
        for _ in range(multi):
            time.sleep(config.settings.KBD_MININTERVAL)
            keyboard.send('left')

    def multi_right(self,multi: int):
        for _ in range(multi):
            time.sleep(config.settings.KBD_MININTERVAL)
            keyboard.send('right')

    def multi_rotate(self,multi: int):
        for _ in range(multi):
            time.sleep(config.settings.KBD_MININTERVAL)
            keyboard.send('e')

# test code if directly run this script
if __name__ == '__main__':
    kc = KeyboardController()

    def test_actions():
        logger.info('keyboard test1')
        #print('\a')  # Beep sound
        #time.sleep(2)
        start_time = time.time()
        '''
        for _ in range(5):
            kc.multi_left(3)
            #time.sleep(1)
            kc.multi_right(3)
            #time.sleep(1)
            kc.multi_rotate(4)
            #time.sleep(1)
            kc.multi_right(3)
            kc.multi_left(3)
            kc.multi_rotate(4)
            kc.press_drop()
        '''
        for _ in range(5):
            kc.multi_left(3)
            kc.multi_rotate(2)
            kc.press_drop()
        for _ in range(5):
            kc.multi_right(3)
            kc.multi_rotate(2)
            kc.press_drop()
        
        elapsed_time = time.time() - start_time
        logger.info(f"Elapsed time for the loop: {elapsed_time:.2f} seconds")
        return

    keyboard.add_hotkey('alt+9', test_actions)
    print("按 Alt+9 测试自动按键...")
    keyboard.wait('q')  # 保持进程，等待热键触发

