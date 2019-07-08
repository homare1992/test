# -*- coding: utf-8 -*-

import os
import subprocess
import pyautogui as pgui
import time
from selenium import webdriver

path = r"C:\VPN専用"
explorer = subprocess.run('explorer {}'.format(path))
time.sleep(3)

pgui.keyDown('winleft')
pgui.keyDown('up')

pgui.keyUp('winleft')
pgui.keyUp('up')

time.sleep(2)

timestr = time.strftime("%Y%m%d")
s = pgui.screenshot()
s.save(r'C:\Users\FU25166\Pictures\画面キャプチャ\画面キャプチャ_{}.jpg'.format(timestr))

path = r'C:\Users\FU25166\Pictures\画面キャプチャ'
explorer = subprocess.run('explorer {}'.format(path))
