import pyautogui

from .actions import *
from .cards import *

def update_supports():
    while True:
        click_wait_img('update')
        wait_img('update-friend-list')

        if click_img('yes'):
            break
        click_wait_img('update-close')

def find_support(supports, max_scrolls=3):
    scrolls = 0
    while True:
        wait_img('update')

        for sup in supports:
            found = click_img(sup)
            if found:
                return
        if scrolls >= max_scrolls:
            update_supports()
            scrolls = 0
            continue
        scroll_wait_img('scroll', 0, 70)
        scrolls += 1

def battle_wave(wave_skills):
    wave_skills = wave_skills.split(';')
    turn = 0
    wait_img('attack')
    retake_img('-battle-num')
    while True:
        print('-'*20)
        print('Turn', turn)
        if turn >= len(wave_skills):
            skills = 'atk'
        else:
            skills = wave_skills[turn].strip()
        if wait_many_img(['attack', 'servant-bond'])[0] == 'servant-bond':
            return False
        if test_changed_img('-battle-num', True):
            return True
        apply_skills(skills)
        use_cards(3, 'abq', alternate=1)
        turn += 1

_coords = lambda y, xs: [(x, y) for x in xs]

SKILLS = {
    'atk': None,
    'np': _coords(200, [425, 650, 900]),
    'm': _coords(300, [900, 1000, 1080]),
    's': _coords(400, [300, 650, 950]),
    '': _coords(575, [75, 160, 260, 390, 480, 575, 700, 800, 900])
}

SEQUENCES = {
    'atk': ('sleep:0.5', 'c:attack', ),
    'np': ('w:back', 'sleep:0.5', 'click:i'),
    'm': ('w:attack', 'c:master-skill', 'sleep:0.5', 'click:i'),
    's': ('w:skill-x', 'click:i'),
    '': ('w:attack', 'click:i', 'sleep:0.5'),
}

ACTIONS = {
    'w': wait_img,
    'c': click_wait_img,
    'sleep': lambda s: time.sleep(float(s))
}

def exec_sequence(arg, seq, positions):
    for a in seq:
        code, option = a.split(':')
        if code != 'click':
            ACTIONS[code](option)
        else:
            index = int(option) if option != 'i' else (int(arg)-1)
            click(positions[index])

def apply_skills(skills):
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
            exec_sequence(s[len(prefix):], SEQUENCES[prefix], positions)
            break

def auto_battle(supports, all_skills):
    click_wait_img('previous')
    find_support(supports)
    click_wait_img('start-quest')

    wait_img('attack')
    retake_img('-battle-num')

    wave = 0
    while True:
        print('='*20)
        print('Wave', wave)
        if wave >= len(all_skills):
            skills = ''
        else:
            skills = all_skills[wave]
        if not battle_wave(skills): break
        wave += 1

    while True:
        if click_img('next'): break
        click((1250, 10))
        time.sleep(1)
    
    wait_img('menu')

    print('done')

def main():
    auto_battle(
        supports=['mona-lisa-mlb'],
        all_skills=['1 3 4 6 m2 s2 atk np2', '2 atk np1', '8 9 atk np3']
    )
    pass

if __name__ == '__main__':
    main()