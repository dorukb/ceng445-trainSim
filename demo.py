import pygame as pygame
from pygame import image
from pygame.locals import *
import trainLib as lib

import time

import cmd, sys
from turtle import *
import threading as th


# globals
globalGrid = None
stopDisplay = False
isDisplaying = False
displayThread = None
isDirty = False

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)

imageWidth = 200
WINDOW_HEIGHT = 800
WINDOW_WIDTH = 800

def rot_center(image, angle):
    loc = image.get_rect().center  
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite


# Reg Reg Rig Lef
# x2S1 x1S3 Lc x2S2
# st br x1S1 Lc
# x3Ri x1S1 Lef Reg
def pygameDisplay(threadName):
    global SCREEN, CLOCK
    pygame.init()
    SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    CLOCK = pygame.time.Clock()
    SCREEN.fill(BLACK)

    # Prepare images to display later.
    regularImg = pygame.image.load("straightRoad.png")

    bgImg = pygame.image.load("bg.png")
    rightImage = pygame.image.load("rightTurn.png")
    switch1Img = pygame.image.load("switch1.png")
    switch2Img = pygame.image.load("switch2.png")
    switch3Img = pygame.image.load("switch3.png")
    levelCrossingImg = pygame.image.load("levelCrossing.png")
    stationImg = pygame.image.load("station.png")
    bridgeImg = pygame.image.load("bridge.png")
    trainImg = pygame.image.load("train.png")

    leftImage = pygame.image.load("rightTurn.png")
    leftImage = rot_center(leftImage, -90)

    topLeftRect = regularImg.get_rect()
    # x2s1Img = pygame.image.load("switch1.png")
    # x2s1Img = rot_center(x2s1Img, -180)
    # x1s3Img = pygame.image.load("switch3.png")
    # x1s3Img = rot_center(x1s3Img, -90)
    # x2s2Img = pygame.image.load("switch2.png")
    # x2s2Img = rot_center(x2s2Img, -180)
    # row 4 images
    # x3rightImg = pygame.image.load("rightTurn.png")
    # x3rightImg = rot_center(x3rightImg, -270)

    global globalGrid
    view = []

    regularImgCache = {0 : regularImg}
    rightImgCache = {0 : rightImage}
    leftImgCache = {0 : leftImage}
    switch1ImgCache = {0: switch1Img}
    switch2ImgCache = {0: switch2Img}
    switch3ImgCache = {0: switch3Img}
    levelCrossingImgCache = {0: levelCrossingImg}
    stationImgCache  = {0 : stationImg}
    bridgeImgCache = {0: bridgeImg}
    trainImgCache = {0: trainImg}

    for i in range(0, globalGrid.row):
        view.append([])
        for j in range(0, globalGrid.col):
            elm = globalGrid.grid[i][j]
            # print(elm, type(elm), isinstance(elm, lib.CellElement))
            if(isinstance(elm,  lib.RegularRoad)):
                if(elm.visuals == '|'):
                    view[i].append(regularImg)
                    # if(elm.rotationCount in regularImgCache):
                    #     # use that img
                    #     view[i].append(regularImgCache[elm.rotationCount])
                    # else:
                    #     #create that img and save it there
                    #     rotatedImg = pygame.image.load("straightRoad.png")
                    #     rotatedImg = rot_center(rotatedImg, -90 * elm.rotationCount)
                    #     regularImgCache[elm.rotationCount] = rotatedImg  
                    #     view[i].append(rotatedImg)

                elif(elm.visuals == 'R'):
                    view[i].append(rightImage)
                elif(elm.visuals == 'L'):
                    view[i].append(leftImage)
                else:
                    view[i].append(bgImg)
            elif(isinstance(elm,  lib.SwitchRoad)):
                if(elm.switchType == 1):
                    view[i].append(switch1Img)
                elif(elm.switchType == 2):
                    view[i].append(switch2Img)
                elif(elm.switchType == 3):
                    view[i].append(switch3Img)
                else:
                    return
                    # print("switch type not set error.")
            elif(isinstance(elm,  lib.LevelCrossing)):
                view[i].append(levelCrossingImg)
            elif(isinstance(elm,  lib.BridgeCrossing)):
                view[i].append(bridgeImg)
            elif(isinstance(elm,  lib.Station)):
                view[i].append(stationImg)
            else: # unknown type of cell
                # print("this is bg")
                view[i].append(bgImg)

    trainRect = trainImg.get_rect()
    i = 0
    global stopDisplay, isDirty
    while stopDisplay == False:

        if(isDirty == True):
            isDirty = False
            for i in range(0, globalGrid.row):
                for j in range(0, globalGrid.col):
                    elm = globalGrid.grid[i][j]
                    # print(elm, type(elm), isinstance(elm, lib.CellElement))
                    if(isinstance(elm,  lib.RegularRoad)):
                        if(elm.visuals == '|'):
                            if(elm.rotationCount in regularImgCache):
                                # use that img
                                view[i][j] = regularImgCache[elm.rotationCount]
                            else:
                                #create that img and save it there
                                rotatedImg = pygame.image.load("straightRoad.png")
                                rotatedImg = rot_center(rotatedImg, -90 * elm.rotationCount)
                                regularImgCache[elm.rotationCount] = rotatedImg  
                                view[i][j] = (rotatedImg)
                        elif(elm.visuals == 'R'):
                            if(elm.rotationCount in rightImgCache):
                                # use that img
                                view[i][j] = rightImgCache[elm.rotationCount]
                            else:
                                #create that img and save it there
                                rotatedImg = pygame.image.load("rightTurn.png")
                                rotatedImg = rot_center(rotatedImg, -90 * elm.rotationCount)
                                rightImgCache[elm.rotationCount] = rotatedImg  
                                view[i][j] = (rotatedImg)
                        elif(elm.visuals == 'L'):
                            if(elm.rotationCount in leftImgCache):
                                # use that img
                                view[i][j] = leftImgCache[elm.rotationCount]
                            else:
                                #create that img and save it there
                                rotatedImg = pygame.image.load("rightTurn.png")
                                rotatedImg = rot_center(rotatedImg, -90 * (elm.rotationCount + 1))
                                leftImgCache[elm.rotationCount] = rotatedImg  
                                view[i][j] = (rotatedImg)
                        else:
                            view[i][j] =(bgImg)
                    elif(isinstance(elm,  lib.SwitchRoad)):
                        if(elm.switchType == 1):
                            if(elm.rotationCount in switch1ImgCache):
                                # use that img
                                view[i][j] = switch1ImgCache[elm.rotationCount]
                            else:
                                #create that img and save it there
                                rotatedImg = pygame.image.load("switch1.png")
                                rotatedImg = rot_center(rotatedImg, -90 * elm.rotationCount)
                                switch1ImgCache[elm.rotationCount] = rotatedImg  
                                view[i][j] = (rotatedImg)
                        elif(elm.switchType == 2):
                            if(elm.rotationCount in switch2ImgCache):
                                # use that img
                                view[i][j] = switch2ImgCache[elm.rotationCount]
                            else:
                                #create that img and save it there
                                rotatedImg = pygame.image.load("switch2.png")
                                rotatedImg = rot_center(rotatedImg, -90 * elm.rotationCount)
                                switch2ImgCache[elm.rotationCount] = rotatedImg  
                                view[i][j] = (rotatedImg)
                        elif(elm.switchType == 3):
                            if(elm.rotationCount in switch3ImgCache):
                                # use that img
                                view[i][j] = switch3ImgCache[elm.rotationCount]
                            else:
                                #create that img and save it there
                                rotatedImg = pygame.image.load("switch3.png")
                                rotatedImg = rot_center(rotatedImg, -90 * elm.rotationCount)
                                switch3ImgCache[elm.rotationCount] = rotatedImg  
                                view[i][j] = (rotatedImg)
                        else:
                            return
                            # print("switch type not set error.")
                    elif(isinstance(elm,  lib.LevelCrossing)):
                        if(elm.rotationCount in levelCrossingImgCache):
                            # use that img
                            view[i][j] = levelCrossingImgCache[elm.rotationCount]
                        else:
                            #create that img and save it there
                            rotatedImg = pygame.image.load("levelCrossing.png")
                            rotatedImg = rot_center(rotatedImg, -90 * elm.rotationCount)
                            levelCrossingImgCache[elm.rotationCount] = rotatedImg  
                            view[i][j] = (rotatedImg)
                    elif(isinstance(elm,  lib.BridgeCrossing)):
                        if(elm.rotationCount in levelCrossingImgCache):
                            # use that img
                            view[i][j] = bridgeImgCache[elm.rotationCount]
                        else:
                            #create that img and save it there
                            rotatedImg = pygame.image.load("bridge.png")
                            rotatedImg = rot_center(rotatedImg, -90 * elm.rotationCount)
                            bridgeImgCache[elm.rotationCount] = rotatedImg  
                            view[i][j] = (rotatedImg)
                    elif(isinstance(elm,  lib.Station)):
                        if(elm.rotationCount in levelCrossingImgCache):
                            # use that img
                            view[i][j] = stationImgCache[elm.rotationCount]
                        else:
                            #create that img and save it there
                            rotatedImg = pygame.image.load("station.png")
                            rotatedImg = rot_center(rotatedImg, -90 * elm.rotationCount)
                            stationImgCache[elm.rotationCount] = rotatedImg  
                            view[i][j] = (rotatedImg)
                    else: # unknown type of cell
                        view[i].append(bgImg)
            # update view


        drawGrid(view, topLeftRect)
        # draw train On top
        # SCREEN.blit(trainImg, trainRect)

        pygame.display.flip()
        pygame.display.update()

        time.sleep(0.02)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif(event.type == KEYDOWN):
                if(event.key == K_q):
                    pygame.quit()
    pygame.quit()

def updateView(view):

    return

def getRect(row, col):
    # global imageWidth
    imageWidth = 200
    x = col * imageWidth
    y = row * imageWidth
    return pygame.Rect(0, 0, x, y)
    
def drawGrid(view, topLeft):
    global globalGrid, SCREEN, imageWidth
    for i in range(0, globalGrid.row):
        for j in range(0, globalGrid.col):
            SCREEN.blit(view[i][j], pygame.Rect.move(topLeft, j * imageWidth, i * imageWidth))



class TurtleShell(cmd.Cmd):
    intro = 'Welcome to the htc_dork shell. Type help or ? to list commands.\n'
    prompt = '(htc_dork) '
    file = None

    def do_test1(self, arg):
        self.do_creategrid("4 5")
        self.do_addelm("1 1 regular")
        self.do_addelm("0 2 switch2")
        self.do_addelm("1 2 bridge")
        self.do_removeelm("1 1")

    def do_rotate(self, arg):
        'Usage: rotate rotationCount(int) row col,  exp:  rotate 2 1 0   to rotate cell at row=1 col =0 180 degrees CW'

        global globalGrid,isDirty
        tupleArgs = parse(arg)
        rotCount = tupleArgs[0]
        row = tupleArgs[1]
        col = tupleArgs[2]

        cell = globalGrid.grid[row][col]
        cell.setOrientation(rotCount)

        # now rotate the visuals as well
        isDirty = True



    def do_removeelm(self, arg):
        'Replace cell with background cell at given row col'
        'Exp usage: removeelm 1 2'
        tupleArgs = parse(arg)
        global globalGrid, isDirty
        globalGrid.removeElement(tupleArgs[0], tupleArgs[1])
        isDirty = True

    def do_creategrid(self, arg):
        'Create grid row x col'
        tupleArgs = parse(arg)
        global globalGrid
        globalGrid = lib.GameGrid(tupleArgs[0], tupleArgs[1])

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
            newElm= lib.LevelCrossing(globalGrid)
        elif(typeStr == "leftturn"):
            newElm = lib.RegularRoad(False, globalGrid)
            newElm.makeLeftTurn()
        elif(typeStr == "rightturn"):
            newElm = lib.RegularRoad(False,globalGrid)
        elif(typeStr == "station"):
            newElm = lib.Station(globalGrid)
        else:
            print("typeOfCell(string) argument is invalid. abort.")
            return
        
        globalGrid.addElement(newElm, row, col)
        global isDirty
        isDirty = True

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

        # Display thread is monitoring this global flag to exit its inf loop.
        if(displayThread is not None):
            print("waiting for display thread to close.")
            stopDisplay = True 
            displayThread.join()
        isDisplaying = False
        stopDisplay = False
        print("display thread stopped. done")

    def do_bye(self, arg):
        self.do_stopdisplay(arg)

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
        if self.file:
            self.file.close()
            self.file = None

def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))
if __name__ == '__main__':
    TurtleShell().cmdloop()




    
# first row rects
# baseRect = regularImg.get_rect()
# rect01 = pygame.Rect.move(baseRect, 200, 0)
# rect02 = pygame.Rect.move(baseRect, 400, 0)
# rect03 = pygame.Rect.move(baseRect, 600, 0)

# #second row rects
# rect10 = pygame.Rect.move(baseRect, 0, 200)
# rect11 = pygame.Rect.move(baseRect, 200, 200)
# rect12 = pygame.Rect.move(baseRect, 400, 200)
# rect13 = pygame.Rect.move(baseRect, 600, 200)


# #third row rects
# rect20 = pygame.Rect.move(baseRect, 0, 400)
# rect21 = pygame.Rect.move(baseRect, 200, 400)
# rect22 = pygame.Rect.move(baseRect, 400, 400)
# rect23 = pygame.Rect.move(baseRect, 600, 400)

# #fourth row rects
# rect30 = pygame.Rect.move(baseRect, 0, 600)
# rect31 = pygame.Rect.move(baseRect, 200, 600)
# rect32 = pygame.Rect.move(baseRect, 400, 600)
# rect33 = pygame.Rect.move(baseRect, 600, 600)

