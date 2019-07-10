import pyautogui
import cv2

import time
from collections import namedtuple

from .config import *
from .actions import *
from .logging import *

l = get_logger(__name__)

CARDS_Y = [450]*5
CARDS_X = [52, 307, 562, 820, 1080]

CARD_W = [150]*5
CARD_H = [50]*5

CARD_TOPS = tuple(zip(CARDS_X, CARDS_Y, CARD_W, CARD_H))

CARD_BOTTOMS = [(x+25,y+115,100,25) for x, y, w, h in CARD_TOPS]

CARD_BOTTOMS_SEARCH = [(x-25, y-10, 150, 60) for x, y, w, h in CARD_BOTTOMS]

def retake_cards(template=False):
    wait_img('back')
    l.debug('screenshotting cards...')
    tops = []
    bottoms = []
    for i, c in enumerate(CARD_TOPS):
        pyautogui.screenshot(f'images/-card-top-{i}.png', g_to_s(c))
        tops.append(cv2.imread(f'images/-card-top-{i}.png'))
        if template:
            bottom = CARD_BOTTOMS[i]
        else:
            bottom = CARD_BOTTOMS_SEARCH[i]
        pyautogui.screenshot(f'images/-card-bottom-{i}.png', g_to_s(bottom))
        bottoms.append(cv2.imread(f'images/-card-bottom-{i}.png'))
    return tops, bottoms

BAQ = ('buster', 'arts', 'quick')

templates = {
    t: cv2.imread(f'images/card-{t}.png') 
    for t in BAQ
}

def similarity(haystack, needle):
    return cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED).max()

Card = namedtuple('Card', 'pos type servant')

def analyse_cards():
    tops, bottoms = retake_cards()
    
    types = []
    for bottom in bottoms:
        types.append(max((t for t in templates.keys()), 
            key=lambda t: similarity(bottom, templates[t])))
    
    tops = [cv2.cvtColor(t, cv2.COLOR_RGB2GRAY) for t in tops]
    servant_groups = []
    for i, top in enumerate(tops):
        if not servant_groups:
            servant_groups.append([top, []])
        val, servants = max( (similarity(img, top[5:-5,5:-5]), servants) for img, servants in servant_groups)
        if val > 0.85:
            servants.append(i)
        else:
            servant_groups.append([top, [i]])
    
    servants = [None]*5
    for i, (_, cards) in enumerate(servant_groups):
        for c in cards:
            servants[c] = i
        
    cards = []
    for i in range(5):
        cards.append(Card(i, types[i], servants[i]))
    return cards

def use_cards(num=3, order='baq', alternate=False):
    start = time.time()
    # lower score = better
    weights = {t: (order.index(t[0])+1)*100 for t in BAQ}

    prev_servant = None
    def sort_key(card):
        w =  weights[card.type]
        if alternate and card.servant == prev_servant:
            w += 1000
        return w

    cards = list(analyse_cards())
    l.debug('cards: %s', cards)
    selected = []
    for i in range(num):
        cards.sort(key=sort_key, reverse=True)
        card = cards.pop()
        selected.append(card)
        prev_servant = card.servant
    
    for card in selected:
        pyautogui.click(*pyautogui.center(g_to_s(CARD_TOPS[card.pos])))
        time.sleep(0.2)
    l.info('clicking: %s', selected)
    l.debug('using cards took %f', start - time.time())
    return selected

if __name__ == '__main__':
    print(use_cards(3, 'abq', True))