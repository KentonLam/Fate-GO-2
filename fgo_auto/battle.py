from .actions import *
import pyautogui

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
    while True:
        if turn >= len(wave_skills):
            skills = ''
        else:
            skills = wave_skills[turn]
        apply_skills(skills)
        click_wait_img('attack')
        turn += 1

SKILLS_X = [75, 160, 260, 390, 480, 575, 700, 800, 900]
SKILLS_Y = [575]*9
SKILLS = tuple(zip(SKILLS_X, SKILLS_Y))

M_SKILLS_X = [900, 1000, 1080]
M_SKILLS_Y = [300]*3
M_SKILLS = tuple(zip(M_SKILLS_X, M_SKILLS_Y))

def apply_skills(skills):
    """
    1-9 are normal skills.
    """
    for s in skills.split():
        wait_img('attack')
        if not s.strip(): continue
        if s.startswith('m'):
            num = int(s[1:])
            click_wait_img('master-skill')
            positions = M_SKILLS
        else:
            num = int(s)
            positions = SKILLS
        click(positions[num-1])
    wait_img('attack')

def auto_battle(supports, all_skills):
    click_wait_img('previous')
    find_support(supports)
    click_wait_img('start-quest')

    wait_img('attack')
    retake_img('-battle-num')

    return

    wave = 0
    while True:
        if wave >= len(all_skills):
            skills = ''
        else:
            skills = all_skills[wave]
        battle_wave(skills)
        wave += 1

def main():
    auto_battle(
        supports=['lunchtime-mlb'],
        all_skills=['1 2; 3']
    )
    pass

if __name__ == '__main__':
    main()