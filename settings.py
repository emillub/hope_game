#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  3 12:25:56 2020

@author: emill0210
"""

from getworkingpath import *

#Game settings
TITLE = 'HOP(e)'
WIDTH = 750
HEIGHT = 700
FPS = 60
FONT_NAME = 'arial'
PLAYER_DATA = 'highscore.txt'

#Colors

BLACK = (0,0,0)
WHITE = (255,255,255)
GREY = (180,180,180)
LIGHT_BLUE=(173,216,230)
ORANGE =[255,179,100]
RED = (255, 125, 125)
GREEN = (169,209,125)

BACKGROUND_COLOR = LIGHT_BLUE
#Plat settings
PLAT_COLORS = [GREEN, ORANGE, RED]
PLAT_FACES = [getworkingpath() + '/multimedia/images/faces/smile3.png',getworkingpath() + '/multimedia/images/faces/meh.png',getworkingpath() + '/multimedia/images/faces/mad.png',getworkingpath() + '/multimedia/images/faces/oh.png']

#Sounds
BREAK_SOUND = getworkingpath() + '/multimedia/sounds/break.mp3'
JUMP_SOUND = getworkingpath() + '/multimedia/sounds/jump.wav'
FALL_SOUND = getworkingpath() + '/multimedia/sounds/fall.wav'


#Player settings
PLAYER_ACC = 0.8
GRAVITY = 1
PLAYER_FRICTION = -0.05
PLAYER_AIRFRICTION = -0
BOUNCE_FACTOR = -25

def loadImages(name,num,folder = getworkingpath() + '/multimedia/images/player/'): #Laster bildene for å animere spilleren
    l = []
    for n in range(1,num+1):
        l.append(folder + str(name)+ ' (' +str(n)+')'+'.png')
    return l

PLAYER_RUN = loadImages('Run',15)
PLAYER_JUMP = loadImages('Jump', 15)
PLAYER_IDLE = loadImages('Idle', 15)
