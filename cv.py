"""
File: cv.py
Author: KuRRe8
Created: 2025-04-05
Description:
    This module provides the ScreenshotProcessor class, which handles all
    image capture and processing tasks related to the Tetris game window.
    It locates the game window, captures the screen, extracts relevant regions
    (PZ - Palletizing Zone, NZ - Next Zone), and identifies block positions and types (CB - Control Block, AB - Aiming Block, FA - Full Area, BA - Blank Area) based
    on specified color ranges.
"""

import config.settings
from _logger import logger

import pygetwindow as gw
import pyautogui
from PIL import Image
import mss
import numpy as np
import cv2
from typing import List, Tuple, Optional, Any
import _utils

class ScreenshotProcessor:
    '''
    First capture the screenshot.
    Then recognize P zone and N zone.
    Then store the game state and next block.
    '''
    def __init__(self):
        self.window_title = config.settings.CV_WINDOW_TITLE
        self.window = None # automatically find the target window when invoking capture()
        self.screenshot: Optional[Image.Image] = None # always store the last screenshot, use other code to gurantee the sc is up to date.
        pass
    
    def glance(self):
        '''
        only for debug
        '''
        self.screenshot.show()
        return
    
    def capture(self):
        if self.window is None:
            windows = gw.getWindowsWithTitle(self.window_title)
            if not windows:
                raise RuntimeError(f"Window '{self.window_title}' not found.")
            self.window = windows[0] # Win32window type, get the first one, since if try to find a window solely by name may reture multiple windows.

        left, top, width, height = self.window.left, self.window.top, self.window.width, self.window.height

        with mss.mss() as sct:
            monitor = {"left": left, "top": top, "width": width, "height": height}
            screenshot = sct.grab(monitor)
            image = Image.fromarray(np.array(screenshot)[:, :, :3][..., ::-1])  # Convert BGR to RGB
        self.screenshot = image
    
    def get_P_zone(self)->Tuple[cv2.typing.MatLike,Tuple[int,int,int,int]]:
        '''
        Palletizing Zone is the main gaming zone, consists of 20 rows and 10 columns.

        Return: coordinate of leftmost topmost, and width height.
        '''
        img_cv = cv2.cvtColor(np.array(self.screenshot), cv2.COLOR_RGB2BGR)
        
        target_color = np.array(config.settings.CV_PZONE_BBOX_COLOR, dtype=np.uint8)
        
        mask = cv2.inRange(img_cv, target_color, target_color)
        #cv2.imshow("Mask", mask)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        coords = cv2.findNonZero(mask)
        if coords is None:
            return img_cv, None

        x, y, w, h = cv2.boundingRect(coords)

        cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        return img_cv, (x, y, w, h)
    
    def get_P_zone_new_state(self) -> cv2.typing.MatLike:
        '''
        In this method, determine which block is filled, and internally update GameState singleton.
        new state is represented by ndarray of 20 rows and 10 columns.
        '''
        pass
    
    def get_N_zone(self) -> Tuple[cv2.typing.MatLike, Tuple[int, int, int, int]]:
        '''
        Next Zone is the area that shows the next block.
        
        Return: the bounding box of the largest connected component in the mask.
        '''
        img_cv = cv2.cvtColor(np.array(self.screenshot), cv2.COLOR_RGB2BGR)
        
        target_color = np.array(config.settings.CV_NZONE_COLOR, dtype=np.uint8)
        
        mask = cv2.inRange(img_cv, target_color, target_color)
        #cv2.imshow("Mask", mask)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        
        # Find contours to identify connected components
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return img_cv, None

        # Find the largest contour by area
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)

        # Draw the bounding box of the largest connected component
        cv2.rectangle(img_cv, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        return img_cv, (x, y, w, h)

if __name__ == '__main__':
    logger.info('cv test')
    logger.info(f'window title is {config.settings.CV_WINDOW_TITLE}')
    sp = ScreenshotProcessor()
    sp.capture()
    #sp.glance()
    img_with_bbox, *co = sp.get_P_zone()
    logger.info(f'PZONE bbox is {co}')
    cv2.imshow("P Zone with Bounding Box", img_with_bbox)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    img_with_bbox, *co = sp.get_N_zone()
    logger.info(f'NZONE bbox is {co}')
    cv2.imshow("N Zone with Bounding Box", img_with_bbox)
    cv2.waitKey(0)
    cv2.destroyAllWindows()