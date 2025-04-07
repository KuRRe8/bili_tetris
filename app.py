"""
File: app.py
Author: KuRRe8
Created: 2025-4-5
Description:
    程序主入口
"""

import multiprocessing # for UI
import threading
import time

from controlpanel import ControlPanel

def thread_play(playevent:threading.Event, closeevent:threading.Event):
    logger.info('thread_play constructed.')
    while True:
        if playevent.wait(0.5):
            import cv
            import alg
            import keyboardctrl
            import _utils
            import controlpanel
            import game
            import time

            sp = cv.ScreenshotProcessor()
            alg.GameState().reset()
            try:
                w = _utils.WindowUtils.find_tetris_window()
                _utils.WindowUtils.bring_to_front(w)
            except:
                logger.warning('Find window failed, stop playing.')
                playevent.clear()
                continue

            while True:
                if not playevent.is_set():
                    break
                if closeevent.is_set():
                    logger.info('Exiting player thread.')
                    return   
                
                # 当正确找到窗口时候，一直循环检测画面，直到出现可游戏画面时候继续往后做决策。
                if not sp.capture():
                    time.sleep(1)
                    continue
                if not sp.get_P_zone_new_state():
                    continue
                if not sp.get_N_zone_new_state():
                    continue

                alg.GameState().up_to_date = True
                spin, row, col = alg.SearchAlgorithm.search()
                destination = col-3 # since the Tetrominoes start from col3 (start from 0)
                if destination < 0:
                    keyboardctrl.KeyboardController.multi_rotate(spin)
                    keyboardctrl.KeyboardController.multi_left(abs(destination))
                else:
                    keyboardctrl.KeyboardController.multi_rotate(spin)
                    keyboardctrl.KeyboardController.multi_right(destination)
                keyboardctrl.KeyboardController.press_drop()

                time.sleep(0.1)# for each decision, we want next capture be accurate, wait for the game update

            if closeevent.is_set():
                logger.info('Exiting player thread.')
                return   

    # while True:
        #if playevent.wait(0.5):
        elif closeevent.is_set():
            logger.info('Exiting player thread.')
            return



def start_play():
    play_event.set()
    logger.debug('Start player listener.')
    pass

def stop_play():
    play_event.clear()
    logger.debug('Stop event set!')
    pass

def exit_routine():
    ui_close_event.set()
    close_event.set()


def start_control_panel(close_event):
    control_panel = ControlPanel(close_event)
    control_panel.start()


if __name__ == '__main__':
    import config.settings
    from _logger import logger
    import _utils


    import keyboardctrl
  
    logger.info('App Starting...')
    play_event = threading.Event()
    close_event = threading.Event()

    ui_close_event = multiprocessing.Event()
    ui_close_event.clear()

    p = threading.Thread(target=thread_play,args=(play_event,close_event,))
    p.start()



    control_panel_process = multiprocessing.Process(target=start_control_panel, args=(ui_close_event,))
    control_panel_process.start()

    keyboardctrl.KeyboardController.assign_hotkey(start_play, stop_play, exit_routine)


    p.join()
    control_panel_process.join()
    keyboardctrl.KeyboardController.cancel_hotkey()
    logger.info('App Exiting...')