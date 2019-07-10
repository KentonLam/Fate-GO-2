GAME_WIDTH = 1280
GAME_HEIGHT = 720

SCREEN_WIDTH = 3000
SCREEN_HEIGHT = 2000

TOP_LEFT_X = 0
TOP_LEFT_Y = 318

FULL_GAME = (TOP_LEFT_X, TOP_LEFT_Y, GAME_WIDTH, GAME_HEIGHT)

def g_to_s(pos):
    pos = list(pos)
    pos[0] += TOP_LEFT_X
    pos[1] += TOP_LEFT_Y
    return tuple(pos)