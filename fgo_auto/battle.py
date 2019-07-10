import pyautogui

from .logging import *
from .actions import *
from .cards import *

_coords = lambda y, xs: [(x, y) for x in xs]

logger = get_logger(__name__)

APPLES = {
    'gold': (400, 300),
    'silver': (400, 450),
    'bronze': (400, 565)
}

SKILLS = {
    'atk': None,
    'np': _coords(200, [425, 650, 900]),
    'swap': _coords(350, [150, 350, 550, 750, 950, 1150]) + [(600, 625)], # swap0 is the ok button
    'm': _coords(300, [900, 1000, 1080]),
    's': _coords(400, [300, 650, 950]),
    't': _coords(40, [50, 280, 525]),
    '': _coords(575, [75, 160, 260, 390, 480, 575, 700, 800, 900])
}

SEQUENCES = {
    'atk': ('sleep:0.5', 'c:attack', ),
    'np': ('w:back', 'sleep:0.5', 'click:i'),
    'swap': ('w:swap-x', 'click:i'),
    'm': ('w:attack', 'c:master-skill', 'sleep:0.5', 'click:i'),
    's': ('w:skill-x', 'click:i'),
    't': ('w:attack', 'click:i'),
    '': ('w:attack', 'click:i', 'sleep:0.3'),
}

ACTIONS = {
    'w': wait_img,
    'c': click_wait_img,
    'sleep': lambda s: time.sleep(float(s))
}

def exec_skill_seq(arg, seq, positions):
    logger.debug('skill sequence: %s, i=%s', seq, arg)
    for a in seq:
        code, option = a.split(':')
        if code != 'click':
            ACTIONS[code](option)
        else:
            index = int(option) if option != 'i' else (int(arg)-1)
            click(positions[index])
        time.sleep(0.1)

def apply_turn_skills(skills):
    """
    1-9 are normal skills.
    m1-3 are master skills.
    s1-3 selects allied targets.
    t1-3 selects targets.
    """
    logger.debug('skills for this turn: %s', skills)
    for s in skills.split():
        s = s.strip()
        if not s: continue
        for prefix, positions in SKILLS.items():
            if not s.startswith(prefix): continue
            exec_skill_seq(s[len(prefix):], SEQUENCES[prefix], positions)
            break

def update_supports():
    while True:
        l.info('updating supports')
        click_wait_img('update')
        wait_img('update-friend-list')

        if click_img('yes'):
            break
        click_wait_img('update-close')

class AutoBattle:
    def __init__(self, *, supports=None, max_scrolls=5, skills=(), card_order='baq', card_alternate=False,
            apples=()):
        self.supports = supports 
        self.max_scrolls = max_scrolls
        self.skills = skills 
        self.card_order = card_order 
        self.card_alternate = card_alternate
        self.apples = apples

        self.w_num = 0 
        self.w_turn = 0

    def find_support(self):
        scrolls = 0
        while True:
            wait_img('update')

            for sup in self.supports:
                found = find_img(sup)
                if found and (not sup.endswith('-mlb') or test_mlb(found)):
                    pyautogui.click(*pyautogui.center(found))
                    return
            raise 2
            if scrolls >= self.max_scrolls:
                update_supports()
                scrolls = 0
                continue
            scroll_wait_img('scroll', 0, 70)
            scrolls += 1

    def get_wave_skills(self):
        try:
            return self.skills[self.w_num]
        except IndexError:
            return ''

    def battle_wave(self):
        wave_skills = self.get_wave_skills().split(';')
        wait_img('attack')
        retake_img('-battle-num')
        while True:
            logger.info('Battle %d, turn %d', self.w_num, self.w_turn)
            if self.w_turn >= len(wave_skills):
                skills = ''
            else:
                skills = wave_skills[self.w_turn].strip()
            
            apply_turn_skills(skills)
            name, pos = wait_many_img(['attack', 'back'])
            if name == 'attack':
                pyautogui.click(*pyautogui.center(pos))
                time.sleep(0.2)
            use_cards(3, self.card_order, alternate=self.card_alternate)

            if wait_many_img(['attack', 'servant-bond', 'bond-up'])[0] != 'attack':
                return False # battle finished.
            if test_changed_img('-battle-num', True):
                return True # wave finished but continue.
            self.w_turn += 1

    def start_battle(self):
        click_wait_img('previous')
        if wait_many_img(('restore-ap', 'update'))[0] == 'restore-ap':
            used_apple = False
            for apple_type in self.apples:
                click(APPLES[apple_type])
                if click_wait_many_img(('apple-ok', ))[0] == 'apple-ok':
                    used_apple = True
                    break 
                time.sleep(1)
            if not used_apple:
                raise RuntimeError('no ap and no apples')
        self.find_support()
        click_wait_img('start-quest')

    def do_battle(self, wave=0, turn=0):
        self.w_num = wave 
        self.w_turn = turn
        l.info('starting main battle')
        wait_img('attack')
        retake_img('-battle-num')

        while True:
            logger.info('Starting battle %d', self.w_num)
            if not self.battle_wave(): 
                break
            self.w_num += 1
            self.w_turn = 0

    def end_battle(self):
        l.info('finishing battle')
        while True:
            name, pos = find_many_img(('next', 'close', 'friend-no', 'menu'))
            if name == 'menu': break
            if pos:
                pyautogui.click(*pyautogui.center(pos))
                l.debug('found and clicked on %s', name)
            else:
                click((1000, 10))
            time.sleep(1)
        
        wait_img('menu')
        logger.info('Ended battle.')

    def run_once(self, wave=0, turn=0):
        self.w_num = wave
        self.w_turn = turn
        logger.info('Starting run.')
        start = time.time()
        self.start_battle() 
        self.do_battle()
        self.end_battle()
        taken = time.time() - start
        logger.info('Run ended, took %f seconds.', taken)
        return taken


def main():
    battle = AutoBattle(
        supports=['lunchtime-mlb'],
        skills=['1 3 4 6 m2 s2 atk np2', '2 atk np1', '8 9 atk np3'],
        # skills=['t2 m3 swap2 swap5 swap0 atk', '2 atk np1', '8 9 atk np3']
        card_order='aqb',
        card_alternate=1,
        apples=('bronze', )
    )
    battle.find_support()

if __name__ == '__main__':
    main()