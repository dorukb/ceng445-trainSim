import pygame as pygame
from pygame import image
from pygame.locals import *
import trainLib as lib

import time

import cmd, sys

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
tell = True

BLACK = (0, 0, 0)
WHITE = (200, 200, 200)

imageWidth = 200
#WINDOW_HEIGHT = 800
#WINDOW_WIDTH = 800

def rot_center(image, angle):
    loc = image.get_rect().center  
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite


# Reg Reg Rig Lef
# x2S1 x1S3 Lc x2S2
# st br x1S1 Lc
# x3Ri x1S1 Lef Reg
def pygameDisplay(threadName, row, col):
    global SCREEN, CLOCK
    pygame.init()
    WINDOW_HEIGHT = row*200
    WINDOW_WIDTH = col*200
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



class TrainSimCell(cmd.Cmd):
    intro = 'Welcome to the TrainSim shell. Type help or ? to list commands.\n'
    prompt = '(trainSim) '
    file = None

    #test cases
    def do_testcase1(self,arg):
        '''
        It tries to create grids at different sizes, get error messages first, finally gives the right command and diplay grid.
        '''
        global tell 
        tell = False
        print("give grid size out of bounds:")
        time.sleep(2)
        self.do_creategrid("9 15")
        time.sleep(2)
        print("\n")
        print("give grid size 0:")
        time.sleep(2)
        self.do_creategrid("0 0")
        time.sleep(2)
        print("\n")
        print("give grid size appropirately:")
        time.sleep(2)
        print("check the opened window ->")
        time.sleep(2)
        self.do_creategrid("4 5")
        self.do_display([])
        time.sleep(1)
        

        tell = True

    def do_getduration(self,arg):
        #For now, it just returns the default value and the direction does not matter as long as it is one of the four main directions. 
        '''
        Usage: Enter coordinates (as row column order) and enter direction (lower-case). Exp: getduration 0 0 north
        '''
        global globalGrid
        dirs = { "north" : 0,  "east" : 1, "south" : 2 , "west" : 3}
        tupleArgs = arg.split()
        row = int(tupleArgs[0])
        col = int(tupleArgs[1])
        entdir = tupleArgs[2]

        if(not globalGrid):
            print("Please create a grid before hand.")
            return

        cell = globalGrid.grid[row][col]

        
        if(entdir in dirs.keys()):
            if(cell.visuals == '_'):
                print("Opps, there is no cell element in that position. Please try again.")
                return
            else:
                duration = cell.getDuration(dirs[entdir])
                print("duration for this cell: ", duration)
        else:
            print("Please enter a valid direction.")

    
    def do_getstop(self,arg):
        '''
        Usage: Enter row col coordinates and entdir. Exp: getstop 0 0 north
        '''
        #For now, it just returns the default value and the direction does not matter as long as it is one of the four main directions. 
        global globalGrid
        dirs = { "north" : 0,  "east" : 1, "south" : 2 , "west" : 3}
        tupleArgs = arg.split()
        row = int(tupleArgs[0])
        col = int(tupleArgs[1])
        entdir = (tupleArgs[2])

        if(not globalGrid):
            print("Please create a grid before hand.")
            return

        cell = globalGrid.grid[row][col]

        

        if(entdir in dirs.keys()):
            if(cell.visuals == '_'):
                print("Opps, there is no cell element in that position.")
                return
            else:
                stopTime = cell.getStop(dirs[entdir])
                print("stop this cell for: ", stopTime, "secs")
                return
        else:
            print("Please enter a valid direction.")
            return
    
    def do_getstatus(self,args):
        '''
        Returns the status of the train if there is one in the given cell.
        Usage: getstatus row col Exp: getstatus 0 0
        '''
        global globalGrid
        global train
        

        tupleArgs = args.split()
        row = int(tupleArgs[0])
        col = int(tupleArgs[1])

        if(not globalGrid):
            print("Please create a grid before hand.")
            return

        cell = globalGrid.grid[row][col]
        
        if(cell.visuals == '_'):
            print("There is no such a cell.")
        else:
            if(globalGrid.hasTrain(row,col)):
                status = train.getStatus()
                print(status)
            else:
                print("The train is not in this cell. Please find it first!")

        return

    def do_test1(self, arg):
        self.do_creategrid("4 5")
        self.do_addelm("1 1 regular")
        self.do_addelm("0 2 switch2")
        self.do_addelm("1 2 bridge")
        self.do_removeelm("1 1")

    def do_rotate(self, arg):
        '''
        Usage: rotate rotationCount(int) row col,  exp:  rotate 2 1 0   to rotate cell at row=1 col =0 180 degrees CW
        '''

        global globalGrid,isDirty
        tupleArgs = arg.split()
        rotCount = int(tupleArgs[0])
        row = int(tupleArgs[1])
        col = int(tupleArgs[2])

        if(not globalGrid):
            print("Please create a grid before hand.")
            return

        cell = globalGrid.grid[row][col]
        cell.setOrientation(rotCount)

        # now rotate the visuals as well
        isDirty = True

    def do_entercell(self, arg):
        '''
        Create and place train at given row col with wagoncount many wagons. Cannot create on empty tiles
        entdir is used to determine which side of the tile the train is. Not visually visible as of now.'
        Usage: createtrain row col wagoncount entdir. Exp: entercell 0 0 2 north
        '''

        global globalGrid, trainPosRow, trainPosCol, isDirty, train
        dirs = { "north" : 0,  "east" : 1, "south" : 2 , "west" : 3}

        args = arg.split()
        row = int(args[0])
        col = int(args[1])
        wagonCount = (int)(args[2])
        entdir = (args[3])

        if(not globalGrid):
            print("Please create a grid before hand.")
            return

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
        '''
        Advance the train using its current cell and dir, entercell must be used first.
        Train disappears if out of bounds, empty tile or unconnected road'
        Usage: advancetrain
        '''
        global globalGrid, trainPosRow, trainPosCol, isDirty, train


        # currCell = globalGrid.grid[train.enginePosRow][train.enginePosCol]
        # nextCell = currCell.nextCell(dirs[entdir])
        # needs mutex sync

        if(not globalGrid):
            print("Please create a grid before hand.")
            return
        canMove = train.advance()
        if(canMove == False):
            trainPosRow = -1
            trainPosCol = -1
            print("either unconnected, empty or out of bounds cell. Train will disappear")
        else:
            trainPosRow, trainPosCol = train.getEnginePos()
        # needs mutex sync

        isDirty = True
        return

    def do_getnextcell(self,arg):
        '''
        It prints the coordinates as row col and the type of the nextcell through entdir. 
        Usage: row col coordinates of currentcell, entdir for nextcell. Exp: 0 0 north
        '''
        dirs = { "north" : 0,  "east" : 1, "south" : 2 , "west" : 3}
        tupleArgs = arg.split()
        global globalGrid
        row = int(tupleArgs[0])
        col = int(tupleArgs[1])
        entdir = tupleArgs[2]
        if(not globalGrid):
            print("Please create a grid before hand.")
            return

        next = globalGrid.grid[row][col].nextCell(dirs[entdir])

        

        if(next is None):
            print("You are trying to access out of the bounds. There is nothing but uncertainty.")
        else:
            print(next.row, next.col, type(next))

    def do_changeswitchstate(self, arg):
        '''
        It changes the state of the switch in order. Every call actives the next part according to CW. 
        Usage: row col, Exp: 0 0 
        '''
        # it gets the next state, the default state is the regular road. It follows the CW order.
        tupleArgs = arg.split()
        global globalGrid
        row = int(tupleArgs[0])
        col = int(tupleArgs[1])

        if(not globalGrid):
            print("Please create a grid before hand.")
            return

        cell = globalGrid.grid[row][col]

        
        if(isinstance(cell, lib.SwitchRoad)):
            cell.switchState()
            print(cell.activePiece)
        else:
            print("The switch you are looking for is not here, please try again.")
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
        '''
        Replace cell with background cell at given row col. Exp: removeelm 1 2
        '''

        tupleArgs = parse(arg)
        global globalGrid, isDirty
        if(not globalGrid):
            print("Please create a grid before hand.")
            return
        globalGrid.removeElement(tupleArgs[0], tupleArgs[1])
        isDirty = True

        
    def do_creategrid(self, arg):
        '''
        Create grid row x col. Exp: creategrid 3 4 
        **Note: Max displayable grid size is 5x9 due to image & screen size.
        '''
        #grid size can be 5 row*9 columns at most because of the screen limitations.

        tupleArgs = parse(arg)
        global globalGrid
        if(tupleArgs[0] <=0 or tupleArgs[1] <= 0):
            print("Sorry I can't print the nothingness :(")
            return
        if(tupleArgs[0] > 5 or tupleArgs[1] > 9):
            print("Sorry, the municipilaty of screen does not allow us to built such a large structure :(")
            return
        globalGrid = lib.GameGrid(tupleArgs[0], tupleArgs[1])

    def do_addelm(self, arg):        
        '''
        It adds the given element at the given position.
        Usage: addelm row col typeOfCell
        typeOfCell(string): regular, switch1, switch2, switch3, bridge, levelcrossing, leftTurn, rightTurn, station
        row,col (ints) are cell position. top left is row=0,col=0
        Exp: addelm 0 0 regular
        '''

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
            print("typeOfCell(string) argument is invalid. Abort.")
            return
        
        globalGrid.addElement(newElm, row, col)
        global isDirty
        isDirty = True

    def do_display(self, arg):
        '''
        Display the grid. You can follow the cahnges as long as you don\'t quit. 
        Please close the screen using stopdisplay command or use bye command the quit the shell.
        '''
        global globalGrid
        if(globalGrid == None):
            print("Please cretae a grid first.")
            return
            

        global isDisplaying, displayThread,tell
        if(isDisplaying == False):
            displayThread = th.Thread(target= pygameDisplay, args=("adim emre", globalGrid.row, globalGrid.col))
            displayThread.start()
            isDisplaying = True
        else:
            if(tell):
                print("display thread is already active. change windows")

    def do_stopdisplay(self, arg):
        '''
        Stop the display and close the window. You can still use the commandline.
        '''
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
        '''
        Close the trainSim window, and exit:  BYE
        '''
        self.do_stopdisplay(arg)

        
        print('Thank you for playing with trains! We hope you had fun :D')
        self.close()
        #bye()
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
    TrainSimCell().cmdloop()