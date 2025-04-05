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
import alg
import keyboardctrl

class ScreenshotProcessor:
    '''
    First capture the screenshot.
    Then recognize P zone and N zone.
    Then store the game state and next block.
    '''
    def __init__(self):
        self.window = None # automatically find the target window when invoking capture()
        
        # this screenshot not modified.
        self.screenshot: Optional[Image.Image] = None # always store the last screenshot, use other code to gurantee the sc is up to date.

        self.annotated_image: Optional[Image.Image] = None # in RGB format, used for debug.
        pass
    
    def glance(self):
        '''
        only for debug
        '''
        self.screenshot.show()
        return
    
    def capture(self):

        logger.debug('capture begin')
        # invoke individually before get_P_zone() and get_N_zone()
        if self.window is None:
            self.window = _utils.WindowUtils.find_tetris_window()
            logger.debug(f"Found window")

        _utils.WindowUtils.bring_to_front(self.window)

        left, top, width, height = self.window.left, self.window.top, self.window.width, self.window.height


        with mss.mss() as sct:
            monitor = {"left": left, "top": top, "width": width, "height": height}
            screenshot = sct.grab(monitor)
            image = Image.fromarray(np.array(screenshot)[:, :, :3][..., ::-1])  # Convert BGR to RGB
        self.screenshot = image
        logger.debug('capture end')
    
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

        Return: preview of annoated image.
        '''
        img_with_bbox, bbox = self.get_P_zone() # here the img_with_bbox is in BGR format.
        if bbox is None:
            raise RuntimeError("P Zone not found.")

        x, y, w, h = bbox
        cell_width_in_pixel_float = w / 10
        cell_height_in_pixel_float = h / 20

        p_zone_mask = np.zeros((20, 10), dtype=np.uint8) # 20 rows and 10 columns
        # Iterate over rows and columns, skipping the top 2 rows
        for row in range(2, 20):
            for col in range(10):
            # Calculate the center of each cell
                center_x = x + col * cell_width_in_pixel_float + cell_width_in_pixel_float / 2
                center_x = round(center_x)
                center_y = y + row * cell_height_in_pixel_float + cell_height_in_pixel_float / 2
                center_y = round(center_y)

                # Get the pixel value at the center
                cell_center_bgr = img_with_bbox[center_y, center_x] # BGR
                # Here we do not match exact color, the backgroud is relativly dark, so we use HSV to match
                # This method can efficiently discard ghost block.
                pixel_HSV = cv2.cvtColor(np.uint8([[cell_center_bgr]]), cv2.COLOR_BGR2HSV)[0][0]
                
                if pixel_HSV[2] < config.settings.CV_BLOCKS_GHOST_HSV_V_THRESHOLD:
                    # Draw a small circle at the center of the cell, indicate the cell is empty
                    radius = min(cell_width_in_pixel_float, cell_height_in_pixel_float) // 6
                    radius = round(radius)
                    cv2.circle(img_with_bbox, (center_x, center_y), radius, (0, 0, 0), -1)
                else:
                    p_zone_mask[row, col] = 1 # 1 means this cell is filled. always ignore first two rows.

        game_state_singleton = alg.GameState()
        # first update board
        game_state_singleton.update_board(p_zone_mask)
        # then update current block
        # match excat color, check the row 1 col 5 color, if it is background color, check row 1 col 6.
        # if both are empty, it means that capture is too late, may it goes down already.

        center_y = y + 0*cell_height_in_pixel_float + cell_height_in_pixel_float / 2
        center_y = round(center_y)
        center_x = x + 4 * cell_width_in_pixel_float + cell_width_in_pixel_float / 2
        center_x = round(center_x)
        cell_center_bgr = img_with_bbox[center_y, center_x] # BGR, here y refers to the picture y, but it is literally x in ndarray.
        
        block_colors_dict = {
            _utils.TetrisBlockType.I: config.settings.CV_BLOCK_I_COLOR,
            _utils.TetrisBlockType.J: config.settings.CV_BLOCK_J_COLOR,
            _utils.TetrisBlockType.L: config.settings.CV_BLOCK_L_COLOR,
            _utils.TetrisBlockType.O: config.settings.CV_BLOCK_O_COLOR,
            _utils.TetrisBlockType.S: config.settings.CV_BLOCK_S_COLOR,
            _utils.TetrisBlockType.T: config.settings.CV_BLOCK_T_COLOR,
            _utils.TetrisBlockType.Z: config.settings.CV_BLOCK_Z_COLOR,
        }

        if not np.all(cell_center_bgr == config.settings.CV_PZONE_BACKGROUND_COLOR):
            for block_type, color in block_colors_dict.items():
                if np.all(cell_center_bgr == color):
                    game_state_singleton.update_current_block(block_type)
                    break
        else:
            # try to find row 1 col 6
            center_x = x + 5 * cell_width_in_pixel_float + cell_width_in_pixel_float / 2
            center_x = round(center_x)
            cell_center_bgr = img_with_bbox[center_y, center_x] # BGR
            if np.all(cell_center_bgr == config.settings.CV_PZONE_BACKGROUND_COLOR):
                logger.info("Cell is background color, no block detected in row 1 col 5 and 6.")
                return img_with_bbox
            for block_type, color in block_colors_dict.items():
                if np.all(cell_center_bgr == color):
                    game_state_singleton.update_current_block(block_type)
                    break

        self.annotated_image = Image.fromarray(cv2.cvtColor(img_with_bbox, cv2.COLOR_BGR2RGB))
        return img_with_bbox
        
    
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
    
    def get_N_zone_new_state(self) -> None:
        '''
        Determine the next block type and update the game state.
        '''

        logger.debug('get_N_zone_new_state')
        img_with_bbox, bbox = self.get_N_zone()
        if bbox is None:
            raise RuntimeError("N Zone not found.")
        x, y, w, h = bbox
        region_of_interest = img_with_bbox[y:y + h, x:x + w]

        # Define the block colors to check against
        block_colors_dict = {
            _utils.TetrisBlockType.I: config.settings.CV_BLOCK_I_COLOR,
            _utils.TetrisBlockType.O: config.settings.CV_BLOCK_O_COLOR,
            _utils.TetrisBlockType.T: config.settings.CV_BLOCK_T_COLOR,
            _utils.TetrisBlockType.S: config.settings.CV_BLOCK_S_COLOR,
            _utils.TetrisBlockType.Z: config.settings.CV_BLOCK_Z_COLOR,
            _utils.TetrisBlockType.J: config.settings.CV_BLOCK_J_COLOR,
            _utils.TetrisBlockType.L: config.settings.CV_BLOCK_L_COLOR,
        }

        max_pixel_sum = 0
        detected_block_type = None

        for item in block_colors_dict.items():
            target_color = np.array(item[1], dtype=np.uint8)
            mask = cv2.inRange(region_of_interest, target_color, target_color)
            pixel_sum = np.sum(mask)  # Sum of pixel intensities in the mask

            if pixel_sum > max_pixel_sum:
                max_pixel_sum = pixel_sum
                detected_block_type = item[0]

        if detected_block_type is None:
            raise RuntimeError("No matching block color found in N Zone.")

        # Update the game state with the detected block type
        game_state_singleton = alg.GameState()
        game_state_singleton.update_next_block(detected_block_type)
        #logger.debug(f'Detected NEXT block type if file cv.py: {detected_block_type}')

def _test_routine1():
    '''
    Test the ScreenshotProcessor class.
    '''
    logger.info('test routine1')
    sp = ScreenshotProcessor()
    alg.GameState().reset()
    _utils.WindowUtils.bring_to_front(_utils.WindowUtils.find_tetris_window())

    for _ in range(6):
        print(f'in the loop{_}')
        import time
        time.sleep(0.1)
        keyboardctrl.KeyboardController.press_drop()
        time.sleep(0.2) # sleep here since a little lantency show the comming one
        # fast drop once before the loop
        sp.capture()
        sp.get_P_zone_new_state()
        sp.get_N_zone_new_state()


if __name__ == '__main__':
    _test_routine1()