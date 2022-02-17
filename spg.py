# -*- coding: utf-8 -*-    
from cv2 import cv2

from os import listdir
from random import randint
from random import random
#import pygetwindow
import numpy as np
import mss
import pyautogui
import time
import sys
import yaml
import os

time.sleep(2)

if __name__ == '__main__':
    stream = open("settings.yaml", 'r')
    c = yaml.safe_load(stream)

ct = c['threshold']

print('Did this help you getting your life back? You can donate to 0x5382520946F1A0387a891DA1F7596ac1D5B0e561')
print('O bot te ajudou a ter sua vida de volta? Você pode doar para 0x5382520946F1A0387a891DA1F7596ac1D5B0e561')

pause = c['time_intervals']['interval_between_moviments']
pyautogui.PAUSE = pause

pyautogui.FAILSAFE = False
ship_clicks = 0
login_attempts = 0
last_log_is_progress = False

def addRandomness(n, randomn_factor_size=None):
    if randomn_factor_size is None:
        randomness_percentage = 0.1
        randomn_factor_size = randomness_percentage * n

    random_factor = 2 * random() * randomn_factor_size
    if random_factor > 5:
        random_factor = 5
    without_average_random_factor = n - randomn_factor_size
    randomized_n = int(without_average_random_factor + random_factor)
    return int(randomized_n)

def moveToWithRandomness(x,y,t):
    pyautogui.moveTo(addRandomness(x,10),addRandomness(y,10),t+random()/2)

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

def load_images():
    file_names = listdir('./imgs/')
    targets = {}
    for file in file_names:
        path = 'imgs/' + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

images = load_images()

def show(rectangles, img = None):
    if img is None:
        with mss.mss() as sct:
            monitor = sct.monitors[0]
            img = np.array(sct.grab(monitor))

    for (x, y, w, h) in rectangles:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)

def clickBtn(img,name=None, timeout=3, threshold = ct['default']):
    if not name is None:
        pass
        # print('waiting for "{}" button, timeout of {}s'.format(name, timeout))
    start = time.time()
    while(True):
        matches = positions(img, threshold=threshold)
        if(len(matches)==0):
            hast_timed_out = time.time()-start > timeout
            if(hast_timed_out):
                if not name is None:
                    pass
                    # print('timed out')
                return False
            # print('button not found yet')
            continue

        x,y,w,h = matches[0]
        pos_click_x = x+w/2
        pos_click_y = y+h/2
        # mudar moveto pra w randomness
        moveToWithRandomness(pos_click_x,pos_click_y,1)
        pyautogui.click()
        return True
        print("THIS SHOULD NOT PRINT")


def printScreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}
        return sct_img[:,:,:3]

def positions(target, threshold=ct['default'],img = None):
    if img is None:
        img = printScreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def scroll():
    commons = positions(images['list-ship'], threshold = ct['commom'])
    if (len(commons) == 0):
        return
    x,y,w,h = commons[len(commons)-1]
    offset_x = 10
    moveToWithRandomness(x+offset_x,y,1)
    if not c['use_click_and_drag_instead_of_scroll']:
        pyautogui.scroll(-c['scroll_size'])
    else:
        pyautogui.dragRel(0,-c['click_and_drag_amount'],duration=1, button='left')

def goToMainScreen():
    #if clickBtn(images['spaceship-ingame']):
        #time.sleep(5)
    if clickBtn(images['base']):
        time.sleep(5)
    if clickBtn(images['spaceship']):
        time.sleep(5)

def login():
    #print('login')
    global login_attempts

    if login_attempts > 3:
        print('oo many login attempts, refreshing')
        login_attempts = 0
        pyautogui.hotkey('ctrl','f5')
        return

    if clickBtn(images['close'], name='closeBtn', timeout = 10):
        print('Close button detected, closing in!')
        time.sleep(5)

    if clickBtn(images['connect-wallet'], name='connectWalletBtn', timeout = 10):
        print('Connect wallet button detected, logging in!')
        login_attempts = login_attempts + 1
        time.sleep(10)

    if clickBtn(images['select-wallet-2'], name='sign button', timeout=8):
        # sometimes the sign popup appears imediately
        login_attempts = login_attempts + 1
        time.sleep(10)
        # print('sign button clicked')
        # print('{} login attempt'.format(login_attempts))
        if clickBtn(images['base'], name='teasureHunt', timeout = 15):
            # print('sucessfully login, treasure hunt btn clicked')
            login_attempts = 0
        return
        # click ok button

    if not clickBtn(images['select-wallet-1-no-hover'], name='selectMetamaskBtn'):
        if clickBtn(images['select-wallet-1-hover'], name='selectMetamaskHoverBtn', threshold  = ct['select_wallet_buttons'] ):
            pass
    else:
        pass

    if clickBtn(images['select-wallet-2'], name='signBtn', timeout = 20):
        login_attempts = login_attempts + 1
        time.sleep(10)
        if clickBtn(images['base'], name='teasureHunt', timeout=25):
            login_attempts = 0

    if clickBtn(images['play'], name='okBtn', timeout=5):
        pass

def sendShipsForWork():
    print('Search for ships to work')
    global ship_clicks

    goToMainScreen()
    verifySendShips()

    empty_scrolls_attempts = int(c['empty_scroll_attemps'])

    while(empty_scrolls_attempts > 0):
        buttonsClicked = 0
        while(clickBtn(images['fight-100'],  threshold = .95) == True):
            buttonsClicked = buttonsClicked + 1
            ship_clicks = ship_clicks + 1
            time.sleep(0.5)

            if ship_clicks == 15:
                clickBtn(images['fight-boss'])
                return

        if buttonsClicked == 0:
            empty_scrolls_attempts = empty_scrolls_attempts - 1

        scroll()
    
    time.sleep(1)
    verifySendShips()

def verifySendShips():
    #print('Verify send ships')
    global ship_clicks
    if ship_clicks >= 10:
        print('time to fly')    
        clickBtn(images['fight-boss'])
        return   

def clearAllShips():
    print('Clearing ships')
    while(clickBtn(images['x-remove-ship'],  threshold = .95) == True):
        time.sleep(0.5)
    
    global ship_clicks
    ship_clicks = 0

def main():
    time.sleep(5)
    t = c['time_intervals']

    windows = []

    last = {
    "login" : 0,
    "send_ships_for_work" : 0,
    "verify_lost_fight" : 0,
    "confirm_win" : 0,
    "change_window" : 0
    }

    while True:
        now = time.time()

        time.sleep(2)

        #só verificar se estiver na tela inicial
        if now - last["send_ships_for_work"] > addRandomness(t['send_ships_for_work'] * 60):
            last["send_ships_for_work"] = now
            sendShipsForWork()

        if now - last["login"] > addRandomness(t['check_for_login'] * 60):
            sys.stdout.flush()
            last["login"] = now
            login()

        if now - last["verify_lost_fight"] > addRandomness(t['verify_lost_fight'] * 60):
            last["verify_lost_fight"] = now
            if clickBtn(images['confirm'],  threshold = .95):
                time.sleep(5)
                global ship_clicks
                ship_clicks = 0
                clickBtn(images['spaceship-ingame'],  threshold = .95)
                time.sleep(5)
                clearAllShips()
                sendShipsForWork()

        if now - last["confirm_win"] > t['confirm_win'] * 10:
            last["confirm_win"] = now
            clickBtn(images['confirm-win'],  threshold = .9,timeout=1)

        sys.stdout.flush()

main()

