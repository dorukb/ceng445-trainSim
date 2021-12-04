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
isDirty = False # needs sync across pygame and cmd threads.
trainPosRow = -1 # needs sync
trainPosCol = -1 # needs sync
train = None

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
    trainRect = pygame.Rect.move(topLeftRect, -200, -200)

    i = 0
    global stopDisplay, isDirty, trainPosRow, trainPosCol
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
            if(trainPosCol != -1 and trainPosRow != -1):
                trainRect = pygame.Rect.move(topLeftRect, trainPosCol * imageWidth, trainPosRow * imageWidth)

        
        drawGrid(view, topLeftRect)
        # draw train On top
        
        SCREEN.blit(trainImg, trainRect)

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
        tupleArgs = arg.split()
        rotCount = int(tupleArgs[0])
        row = int(tupleArgs[1])
        col = int(tupleArgs[2])

        cell = globalGrid.grid[row][col]
        cell.setOrientation(rotCount)

        # now rotate the visuals as well
        isDirty = True

    def do_entercell(self, arg):
        'Create and place train at given row col with wagoncount many wagons. Cannot create on empty tiles'
        'entdir is used to determine which side of the tile the train is. not visually visible as of now.'
        'Usage: createtrain row col wagoncount entdir'
        global globalGrid, trainPosRow, trainPosCol, isDirty, train
        dirs = { "north" : 0,  "east" : 1, "south" : 2 , "west" : 3}

        args = arg.split()
        row = int(args[0])
        col = int(args[1])
        wagonCount = (int)(args[2])
        entdir = (args[3])

        if(globalGrid.grid[row][col].visuals == '_'):
            print("Can not spawn on empty tile.")
            return

        # TODO: lock train mutex
        train = globalGrid.spawnTrain(wagonCount, row, col)
        train.enterCell(globalGrid.grid[row][col], dirs[entdir])
        trainPosRow, trainPosCol = train.getEnginePos()
        # unlock train mutex

        isDirty = True
        return

    def do_advancetrain(self, arg):
        'Advance the train using its current cell and dir, createtrain must be used first.'
        'Train disappears if out of bounds or unconnected road'
        'Usage: advancetrain'
        global globalGrid, trainPosRow, trainPosCol, isDirty, train

        # currCell = globalGrid.grid[train.enginePosRow][train.enginePosCol]
        # nextCell = currCell.nextCell(dirs[entdir])
        # needs mutex sync
        canMove = train.advance()
        if(canMove == False):
            trainPosRow = -1
            trainPosCol = -1
            print("either unconnected or out of bounds cell. train will disappear")
        else:
            trainPosRow, trainPosCol = train.getEnginePos()
        # needs mutex sync

        isDirty = True
        return

    def do_getnextcell(self,arg):
        'Usage: row col entdir'
        dirs = { "north" : 0,  "east" : 1, "south" : 2 , "west" : 3}
        tupleArgs = arg.split()
        global globalGrid
        row = int(tupleArgs[0])
        col = int(tupleArgs[1])
        entdir = tupleArgs[2]
        print(entdir)
        next = globalGrid.grid[row][col].nextCell(dirs[entdir])
        if(next is None):
            print("out of bounds")
        else:
            print(next.row, next.col, type(next))

    def do_changeswitchstate(self, arg):
        'Usage: row col '
        # it gets the next state default regular
        tupleArgs = arg.split()
        global globalGrid
        row = int(tupleArgs[0])
        col = int(tupleArgs[1])
        cell = globalGrid.grid[row][col]
        if(isinstance(cell, lib.SwitchRoad)):
            cell.switchState()
            print(cell.activePiece)
        else:
            print("There is no switch at given position")
        return
    def do_test2(self, arg):
        'it tests switch state'
        self.do_creategrid("4 4")
        self.do_addelm("0 0 regular")
        self.do_addelm("0 1 regular")
        self.do_addelm("0 2 regular")
        self.do_addelm("2 0 regular")
        self.do_addelm("1 0 switch3")
        self.do_addelm("1 1 switch2")
        self.do_addelm("1 2 switch1")
        print("next cell when enter south:")
        self.do_getnextcell("1 0 south")

        print("next cell when enter east:")
        self.do_getnextcell("1 0 east")

        print("next cell when change state 1 time:")
        # self.do_changeswitchstate("1 0")
        # self.do_getnextcell("1 0 south")
        # print("next cell when rotate:")
        # self.do_rotate("1 1 0")
        # self.do_getnextcell("1 0 west")

        
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

        'Stop recording, close the trainSim window, and exit:  BYE'
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