import pyautogui
import cv2

import os
import time
import pathlib
from collections import namedtuple

from .config import *

IMAGES = {} 
ImgData = namedtuple('ImgData', 'name file position')

center = pyautogui.center

def load_images(fp):
    fp = pathlib.Path(fp)
    for f in os.listdir(fp):
        fname = f
        f = fp / fname
        if os.path.isfile(f) and '---' in fname:
            name, pos = fname.split('.')[0].split('---')
            IMAGES[name] = ImgData(name, str(f.absolute()), tuple(map(int, pos.split(','))))

def retake_img(name):
    img = IMAGES[name]
    pyautogui.screenshot(img.file, g_to_s(img.position))

def test_changed_img(name):
    img = IMAGES[name]
    old = cv2.imread(img.file).copy()
    retake_img(name)
    new = cv2.imread(img.file).copy()
    similar = abs(float(cv2.matchTemplate(old, new, cv2.TM_CCOEFF_NORMED)))
    return similar < 0.5 

def locate(img_data, **kwargs):
    pos = list(img_data.position)
    pos = g_to_s(pos)
    # pos[2] += pos[0]
    # pos[3] += pos[1]
    # print(pos)
    print(img_data)
    result = (pyautogui.locateOnScreen(img_data.file, confidence=0.90, **kwargs))
    print('    ', result)
    return result

def wait_img(name):
    assert name in IMAGES
    while True:
        result = locate(IMAGES[name])
        if result: return result
        time.sleep(0.5)

def click_wait_img(name):
    pyautogui.click(pyautogui.center(wait_img(name)))

def find_img(name):
    return locate(IMAGES[name])

def click_img(name):
    pos = locate(IMAGES[name])
    if pos:
        pyautogui.click(*center(pos))
    return pos

def click(game_pos):
    pyautogui.click(*(g_to_s(game_pos)))

def scroll_wait_img(name, dx, dy):
    pos = center(wait_img(name))
    pyautogui.moveTo(*pos)
    pyautogui.dragRel(dx, dy, duration=1)


load_images('images')
if __name__ == '__main__':
    wait_img('menu')