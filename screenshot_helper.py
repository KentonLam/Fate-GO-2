import pyautogui
from PIL import Image, ImageDraw

import time
import os

from fgo_auto import FULL_GAME, GAME_HEIGHT, GAME_WIDTH

def screenshot(filename, position):
    print(f'Taking screenshot {filename} at {position}.')
    pyautogui.screenshot('images/'+filename, position)

def grid_screenshot():
    filename = 'main.png'
    screenshot(filename, FULL_GAME)
    img = Image.open('images/'+filename)
    img2 = img.copy()
    d = ImageDraw.Draw(img)

    draw_horizontal = lambda w, w2, colour: [(d.line([(x,0), (x, GAME_HEIGHT)], fill=colour, width=w2), d.text((x+5, 10), str(x))) for x in range(0, GAME_WIDTH, w)]
    draw_vertical = lambda w, w2, colour: [(d.line([(0,y), (GAME_WIDTH,y)], fill=colour, width=w2), d.text((10, y+5), str(y))) for y in range(0, GAME_HEIGHT, w)]

    draw_horizontal(50, 1, (50,0,0))
    draw_horizontal(100, 1, (128,0,0))
    draw_horizontal(200, 5, (255,0,0))

    draw_vertical(50, 1, (0,50,0))
    draw_vertical(100, 1, (0,128,0))
    draw_vertical(200, 5, (0,255,0))    
        
    img.save('images/main_grid.png')
    return img2

def crop_snapshot(name, img):
    snapshot = input(f'{name} position: >>> ')
    snapshot = tuple(map(int, snapshot.strip().split()))
    snapshot2 = list(snapshot)
    snapshot2[2] += snapshot[0]
    snapshot2[3] += snapshot[1]
    snapshot2 = tuple(snapshot2)

    search = input(f'{name} search box? >>> ').strip()
    if not search:
        buffer = 10
        search = [snapshot[0]-buffer, snapshot[1]-buffer, snapshot[2]+2*buffer, snapshot[3]+2*buffer]
    else:
        search = (search.strip().split())
    search = list(map(int, search))
    search[0] = max(0, search[0])
    search[1] = max(0, search[1])
    search[2] = min(GAME_WIDTH-search[0]-1, search[2])
    search[3] = min(GAME_HEIGHT-search[1]-1, search[3])
    search = tuple(map(str, search))

    img = img.copy()
    img_crop = img.crop(snapshot2)
    print(snapshot2)
    filename = f'images/{name}---{",".join(search)}.png'
    img_crop.save(filename)

    result = bool(input('Blank to try again...').strip())
    if not result:
        os.unlink(filename)
    return result

def screenshot_helper():
    while True:
        print()
        print('='*30)
        img = grid_screenshot()
        name = input('Name: ').strip()
        if not name: continue
        while True:
            try:
                if crop_snapshot(name, img):
                    break
            except KeyboardInterrupt:
                print('Interrupt.')       
        


def main():
    # time.sleep(3)
    screenshot_helper()

if __name__ == '__main__':
    main()