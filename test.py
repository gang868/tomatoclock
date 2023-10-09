#!/usr/bin/python3
# -*- coding: utf-8 -*-

import playsound, os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def playSound(fileName):
    try:
        playsound.playsound(os.path.join(BASE_DIR, fileName))
        # playsound.playsound("bark.ogg")
    except Exception as ex:
        print("playsound exception:", ex)

if __name__ == '__main__':
    # playSound('bark.ogg')
    playSound("bark.mp3")
    playSound("drip.mp3")
