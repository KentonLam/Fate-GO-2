import pyautogui

from .actions import *
from .cards import *

_coords = lambda y, xs: [(x, y) for x in xs]

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
    for s in skills.split():
        s = s.strip()
        if not s: continue
        for prefix, positions in SKILLS.items():
            if not s.startswith(prefix): continue
            exec_skill_seq(s[len(prefix):], SEQUENCES[prefix], positions)
            break

def update_supports():
    while True:
        click_wait_img('update')
        wait_img('update-friend-list')

        if click_img('yes'):
            break
        click_wait_img('update-close')

class AutoBattle:
    def __init__(self, *, supports=None, max_scrolls=3, skills=(), card_order='baq', card_alternate=False):
        self.supports = supports 
        self.max_scrolls = max_scrolls
        self.skills = skills 
        self.card_order = card_order 
        self.card_alternate = card_alternate

        self.w_num = 0 
        self.w_turn = 0

    def find_support(self):
        scrolls = 0
        while True:
            wait_img('update')

            for sup in self.supports:
                found = click_img(sup)
                if found:
                    return
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
            print('-'*20)
            print('Battle', self.w_num, 'turn', self.w_turn)
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
        while wait_many_img(('restore-ap', 'update'))[0] == 'restore-ap':
            print('no ap')
            return
        self.find_support()
        click_wait_img('start-quest')

    def do_battle(self, wave=0, turn=0):
        self.w_num = wave 
        self.w_turn = turn

        wait_img('attack')
        retake_img('-battle-num')

        while True:
            print('='*20)
            print('Wave', self.w_num)
            if not self.battle_wave(): 
                break
            self.w_num += 1
            self.w_turn = 0

    def end_battle(self):
        while True:
            name, pos = find_many_img(('next', 'close', 'friend-no', 'menu'))
            if name == 'menu': break
            if pos:
                pyautogui.click(*pyautogui.center(pos))
            else:
                click((1000, 10))
            time.sleep(1)
        
        wait_img('menu')

        print('done')

    def run_once(self):
        start = time.time()
        self.start_battle()
        self.do_battle()
        self.end_battle()
        return time.time() - start


def main():
    battle = AutoBattle(
        supports=['mona-lisa-mlb'],
        skills=['1 3 4 6 m2 s2 atk np2', '2 atk np1', '8 9 atk np3'],
        # skills=['t2 m3 swap2 swap5 swap0 atk', '2 atk np1', '8 9 atk np3']
        card_order='aqb',
        card_alternate=1
    )
    battle.do_battle()

if __name__ == '__main__':
    main()