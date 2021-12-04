import pygame as pygame
import sys
from pygame.locals import *
import trainLib as lib

# from trainLib import GameGrid, RegularRoad
import time
pygame.BLEND_RGBA_SUB

import cmd, sys
from turtle import *
import threading as th


# globals
globalGrid = None
stopDisplay = False

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800

regularImg = pygame.image.load("straightRoad.png")
# first row rects
baseRect = regularImg.get_rect()
rect01 = pygame.Rect.move(baseRect, 200, 0)
rect02 = pygame.Rect.move(baseRect, 400, 0)
rect03 = pygame.Rect.move(baseRect, 600, 0)

#second row rects
rect10 = pygame.Rect.move(baseRect, 0, 200)
rect11 = pygame.Rect.move(baseRect, 200, 200)
rect12 = pygame.Rect.move(baseRect, 400, 200)
rect13 = pygame.Rect.move(baseRect, 600, 200)


#third row rects
rect20 = pygame.Rect.move(baseRect, 0, 400)
rect21 = pygame.Rect.move(baseRect, 200, 400)
rect22 = pygame.Rect.move(baseRect, 400, 400)
rect23 = pygame.Rect.move(baseRect, 600, 400)

#fourth row rects
rect30 = pygame.Rect.move(baseRect, 0, 600)
rect31 = pygame.Rect.move(baseRect, 200, 600)
rect32 = pygame.Rect.move(baseRect, 400, 600)
rect33 = pygame.Rect.move(baseRect, 600, 600)

def rot_center(image, angle):
    loc = image.get_rect().center  
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite

imageWidth = 200
rightRect = pygame.Rect.move(baseRect, 200, 0)
switch1Rect = pygame.Rect.move(baseRect, 0, 200)
switch2Rect = pygame.Rect.move(baseRect, 200, 200)

bgImg = pygame.image.load("bg.png")
rightImage = pygame.image.load("rightTurn.png")
switch1Img = pygame.image.load("switch1.png")
switch2Img = pygame.image.load("switch2.png")
switch3Img = pygame.image.load("switch3.png")
levelCrossingImg = pygame.image.load("levelCrossing.png")


# row 2 images
leftImage = pygame.image.load("rightTurn.png")
leftImage = rot_center(leftImage, -90)

x2s1Img = pygame.image.load("switch1.png")
x2s1Img = rot_center(x2s1Img, -180)

x1s3Img = pygame.image.load("switch3.png")
x1s3Img = rot_center(x1s3Img, -90)

x2s2Img = pygame.image.load("switch2.png")
x2s2Img = rot_center(x2s2Img, -180)


# row 3 images
stationImg = pygame.image.load("station.png")
bridgeImg = pygame.image.load("bridge.png")
x1s1Img = pygame.image.load("switch1.png")
x1s1Img = rot_center(x1s1Img, -90)

# row 4 images
x3rightImg = pygame.image.load("rightTurn.png")
x3rightImg = rot_center(x3rightImg, -270)


# Reg Reg Rig Lef
# x2S1 x1S3 Lc x2S2
# st br x1S1 Lc
# x3Ri x1S1 Lef Reg

firstRowImgs = [regularImg, regularImg, rightImage, leftImage]

def pygameDisplay(threadName):
    global SCREEN, CLOCK
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(BLACK)


    cellVisuals = {}
    
    global globalGrid
    # grid = lib.GameGrid(4,4)
    # grid.display()

    # regCell = lib.RegularRoad(True,grid)
    # cellVisuals[regCell] = regularImg
    # d['mynewkey'] = 'mynewvalue'
    # imgs = []
    # imgs.append((regularImg,baseRect))

    trainImg = pygame.image.load("train.png")
    trainRect = trainImg.get_rect()

    i = 0
    secondRowImgs = []

    global stopDisplay
    while stopDisplay == False:
        drawGrid()
        # draw train On top
        SCREEN.blit(trainImg, trainRect)

        pygame.display.flip()
        pygame.display.update()

        if(i < 4):
            pygame.Rect.move_ip(trainRect, 200, 0)
            i += 1
        else:
            pygame.Rect.move_ip(trainRect, -800, 200)
            i = 0

        time.sleep(1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                # sys.exit()
            elif(event.type == KEYDOWN):
                if(event.key == K_p):
                    print("pressed P")

                if(event.key == K_q):
                    pygame.quit()
    pygame.quit()

def drawGrid():
    # draw first row
    SCREEN.blit(firstRowImgs[0], baseRect)
    SCREEN.blit(firstRowImgs[1], rect01)
    SCREEN.blit(firstRowImgs[2], rect02)
    SCREEN.blit(firstRowImgs[3], rect03)

    # draw second row
    SCREEN.blit(x2s1Img, rect10)
    SCREEN.blit(x1s3Img, rect11)
    SCREEN.blit(levelCrossingImg, rect12)
    SCREEN.blit(x2s2Img, rect13)

    # draw third row
    SCREEN.blit(x2s1Img, rect20)
    SCREEN.blit(bridgeImg, rect21)
    SCREEN.blit(x1s1Img, rect22)
    SCREEN.blit(levelCrossingImg, rect23)

    # draw last row
    SCREEN.blit(x3rightImg, rect30)
    SCREEN.blit(x1s1Img, rect31)
    SCREEN.blit(leftImage, rect32)
    SCREEN.blit(stationImg, rect33)

# main()


isDisplaying = False
displayThread = None

class TurtleShell(cmd.Cmd):
    intro = 'Welcome to the htc_dork shell. Type help or ? to list commands.\n'
    prompt = '(htc_dork) '
    file = None

    # ----- basic turtle commands -----

    def do_test1(self, arg):
        self.do_creategrid("4 5")
        self.do_addelm("1 1 regular")
        self.do_addelm("0 2 switch2")
        self.do_addelm("1 2 bridge")

    def do_creategrid(self, arg):
        'Create grid row x col'
        tupleArgs = parse(arg)
        global globalGrid
        globalGrid = lib.GameGrid(tupleArgs[0], tupleArgs[1])
        # globalGrid.display()

    def do_addelm(self, arg):        
        '''Usage: addelm row col typeOfCell
        typeOfCell(string): regular, switch1, switch2, switch3, bridge, levelcrossing, leftTurn, rightTurn, station
        row,col (ints) are cell position. top left is row=0,col=0'''
        splitArgs = arg.split()
        row = int(splitArgs[0])
        col = int(splitArgs[1])
        typeStr = splitArgs[2]

        global globalGrid
        if(globalGrid is None):
            print("Please first create a grid.")
            return

        newElm = None
        if(typeStr == "regular"):
            print("regular is chosen.")
            newElm = lib.RegularRoad(True, globalGrid)
        elif(typeStr == "switch1"):
            newElm = lib.SwitchRoad(1, globalGrid)
        elif(typeStr == "switch2"):
            newElm = lib.SwitchRoad(2, globalGrid)
        elif(typeStr == "switch3"):
            newElm = lib.SwitchRoad(3, globalGrid)
        elif(typeStr == "bridge"):
            newElm = lib.BridgeCrossing(globalGrid)
        elif(typeStr == "levelcrossing"):
            newElem = lib.LevelCrossing(globalGrid)
        elif(typeStr == "lefTurn"):
            newElem = lib.RegularRoad(False, globalGrid)
            newElem.makeLeftTurn()
        elif(typeStr == "rightTurn"):
            newElem = lib.RegularRoad(False,globalGrid)
        elif(typeStr == "station"):
            newElem = lib.Station(globalGrid)
        else:
            print("typeOfCell(string) argument is invalid. abort.")
            return
        
        globalGrid.addElement(newElm, row, col)
        # print("Grid after the addition of", typeStr, "to", row, col)
        # globalGrid.display()

    def do_display(self, arg):
        global globalGrid
        if(globalGrid != None):
             globalGrid.display()

        global isDisplaying, displayThread
        if(isDisplaying == False):
            displayThread = th.Thread(target= pygameDisplay, args=("adim emre",))
            displayThread.start()
            isDisplaying = True
        else:
            print("display thread is already active. change windows")

    def do_stopdisplay(self, arg):
        global stopDisplay, isDisplaying, displayThread
        if(isDisplaying == False): 
            return

        # Display threadh is monitoring this global flag to exit its inf loop.
        
        if(displayThread is not None):
            print("waiting for display thread to close.")
            stopDisplay = True 
            displayThread.join()
        isDisplaying = False
        stopDisplay = False
        print("display thread stopped. done")

    def do_bye(self, arg):
        self.do_stopdisplay(self, arg)

        'Stop recording, close the turtle window, and exit:  BYE'
        print('Thank you for using Turtle')
        self.close()
        bye()
        return True

    def precmd(self, line):
        line = line.lower()
        if self.file and 'playback' not in line:
            print(line, file=self.file)
        return line
    def close(self):
        stopDisplay = True
        if self.file:
            self.file.close()
            self.file = None

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))
if __name__ == '__main__':
    TurtleShell().cmdloop()
