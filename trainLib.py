import math
import time

#constants and globals
background = '0'
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

dirs = {0 : "NORTH", 1 : "EAST", 2 : "SOUTH", 3 : "WEST"}

class CellElement(): #CellELement Interface for the subclasses

    #Subclasses: RegularRoad, Switch, LevelCrossing, Bridge, Station

    def setPosition(self, x, y):
        return
    def setOrientation(self, a):
        return
    def switchState(self):
        return
    def getDuration(self, entdir):
        return
    def getStop(self, entdir):
        return
    def nextCell(self,entdir):
        return   
    def getView():
        return

    # Additional Interface methods added by us
    def setCwRot(self):
        return
    def canEnter(self, entdir): # it checks the availability of the next cell in case of there is another train.
        return
    def getPos(self):
        return
    
class GameGrid():
    
    def __init__ (self, row, col):
        self.row = row
        self.col = col
        self.grid = []
        self.view = []
        
        self.simTime = 0
        self.timeStep = 1 
        self.isPaused = False
        self.isRunning = False
        # Train refs to draw them on screen, on top of the tile view.
        self.activeTrains = []
        #default grid creation filled with background 
        for i in range(0, row):
            self.grid.append([])
            self.view.append([])
            for j in range(0, col):
                c = RegularRoad(True, self.grid) 
                #Eventhough it assigns a RegularRoad to every cell, we make it background changing the visuals of the cell. (bkz. CellElement.visuals)
                #We choose it to implemet that way to avoid a creation for empty subclass for background cells and not to make code more complex.
                c.visuals = '_'
                c.setPosition(i,j)
                self.grid[i].append(c)
                #view grid is seperate than the actual grid. It keeps the visulas and used for display issues.
                self.view[i].append(c.visuals)


    def addElement(self, cellElm, row, col):
        cellElm.setPosition(row, col)
        self.grid[row][col] = cellElm
        self.view[row][col] = cellElm.visuals
        return

    def removeElement(self, row, col):
        empty = RegularRoad(True, self.grid) # (bkz. GameGrid.__init___ (): line 51)
        empty.visuals = '_'
        self.grid[row][col] = empty
        self.view[row][col] = '_' # visual for background
        return

    def display(self):
        for i in range(0,self.row):
            for j in range(0, self.col):
                print(self.view[i][j], end=' ')
            print('\n')

    def isOutOfBounds(self, i, j): #check whether the given positions exists or not
        if(i >= self.row or j >= self.col or i < 0 or j < 0): 
            return True
        return False

    def updateView(self): # We provide this functionality by updtaing the view grid and display function where it needed.  
        return

    def startSimulation(self): 
        self.simTime = 0
        self.isRunning = True

        while self.isRunning:

            if(not self.isPaused):
                self.simTime += self.timeStep
                for train in self.activeTrains:
                    if(train):
                        print("sim advanced one more tick")
                        train.tick()

            time.sleep(self.timeStep)
        return

    def setPauseResume(self):
        self.isPaused = not self.isPaused
        return

    def stopSimulation(self):
        self.isRunning = False
        return
    
    def spawnTrain(self, wagonCount, row, col): # Creates trains at given row and column

        if(self.isOutOfBounds(row,col)):
            print("invalid spawn pos for train.", row, col)
            return
        
        spawnCell = self.grid[row][col]
        t = Train(wagonCount, spawnCell, self)
        self.registerTrain(t) # register train for the grid. 
                              #For the phase1 it is not that functional but when we have more trains in later phases it will be used as it supposed to.
        
        return t

    def registerTrain(self, train):
        print('train registered')
        self.activeTrains.append(train)
        return

    def trainDisappear(self,train):
        print('train removed')
        
        try:
            self.activeTrains.remove(train)
        except:
            print('train not found')

        return

    def hasTrain(self, row, col):  #it checks whether there is a train in the given cell or not 
        for t in self.activeTrains:
            if(t.enginePosRow == row and t.enginePosCol == col):
                 return True
        return False

class RegularRoad(CellElement):
    # RegularRoad can be either a straight road or a right turn.
    # We class them as this since they both have one entrance and exit.

    def __init__(self, isStraight, gridRef):
        self.visuals = '_'
        self.rotationCount = 0
        self.myGrid = gridRef    #needs grid reference since we have to reach there to update grid.
        self.row = -1
        self.col = -1
        self.isRegular = isStraight # if it is not straigt, it is a right turn. We exclude left turn here since it is the one time rotated version of right turn.
                                    # For the sake of simplicity, we define left turn by rotating the right turn.
        
        if(isStraight):
            self.dir1 = SOUTH
            self.dir2 = NORTH
            self.visuals = '|'
        else:                       # default is a Right turn as in the pdf.
                                    # rotate this one time CW to get a left turn if needed
            self.visuals = 'R'
            self.dir1 = SOUTH
            self.dir2 = EAST
        return

    def makeLeftTurn(self): # used for make a left turn from a right turn.
        self.visuals = 'L'
        self.rotationCount = 0  # When we rotate to get left turn the count has been increased.
                                # rotation count is assigned to 0 again since it should be a base case. 
        self.setOrientation( 1, False)
        return self

    def setPosition(self, row, col):
        self.row = row
        self.col = col
        return

    def setCwRot(self):   #it assigns the new directions CW of the roads.
        self.dir1 = (self.dir1 + 1) % 4
        self.dir2 = (self.dir2 + 1) % 4
        return

    def setOrientation(self, rotationAmount, incrRot : bool = True): #if incrRot is given False, it doesn't update the rotation amount. It is used for left turn object orientation. 
        if(incrRot):
            self.rotationCount = (self.rotationCount + rotationAmount) % 4 # else assign the value in mod 4 to be able to detect new directions correctly.
        for i in range(0, rotationAmount):
            self.setCwRot()                                            #does the real job 
        return

    def switchState(self):
        return
    def getDuration(self, entdir): # default 1 for Regular Road
        return 1
    def getStop(self, entdir): # default 0 for Regular Road since not stop there
        return 0 

    def nextCell(self,entdir):
        # if on the edge cells, and dir is outward, train will disappear
        # calculate exit direction of the cell using dir values.

        self.exitDir = None  
        #if the given direction is the dir1 assign dir2 as exitDir and vice verca.
        if(self.dir1 == entdir):
            self.exitDir = self.dir2
        elif self.dir2 == entdir:
            self.exitDir = self.dir1
        else: # if the given direction is not valid, exit
            return None

        #According to exitDir, if the nextCell is not out of bounds, return the nextCell
        if(self.exitDir == NORTH and self.myGrid.isOutOfBounds(self.row-1, self.col) == False):
        #     # row-1, col unchanged
            return(self.myGrid.grid[self.row-1][self.col] )
        elif(self.exitDir == SOUTH and self.myGrid.isOutOfBounds(self.row+1, self.col) == False):
        #     # row+1, col unchanged
            return(self.myGrid.grid[self.row+1][self.col])
        elif(self.exitDir == WEST and self.myGrid.isOutOfBounds(self.row, self.col-1) == False):
        #     #  col-1, row unchanged
            return(self.myGrid.grid[self.row][self.col-1])
        elif(self.exitDir == EAST and self.myGrid.isOutOfBounds(self.row, self.col+1) == False):
        #     #  col+1, row unchanged
            return(self.myGrid.grid[self.row][self.col+1])            
        else: #  no available cell is found
            return None

    def getPos(self):
        return self.row, self.col
    def getView(self):
        return  self.visuals
    def canEnter(self, entdir): 
         #check the availability / connectivity of nextcell
        return (self.dir1 == entdir or self.dir2 == entdir)

class SwitchRoad(CellElement):
    #There are three types of switchRoad. Explained in lines:237, 241, 246
    def __init__(self, typeofSwitch, gridRef):
        # create 'pieces' of the switch using RegularRoad since switches are just the combinations of them.
        self.visuals = 'S'
        self.myGrid = gridRef
        self.rotationCount = 0
        self.switchType = typeofSwitch # int value 1,2,3
        self.pieces = {'direct' : RegularRoad(True, gridRef)} #We kept the pieces of the switches according to its type.
                                                              #for example, switchType-3 has one direct, one rightTurn and one leftTurn.
                                                              #since all switches has one RegulaarRoad in common, it is added the dictionary by default.
        
        self.activePiece = self.pieces['direct']              # Keeps track of which part of the switch is active. 
                                                              #Changed by switchState(). Defualt straight piece is the active one.
        
        self.enter = SOUTH                                #default switch entrance location is south for all type of switches
        
        self.switchDelay = 2                                  #used for make train slower in switches. 
        
        if(self.switchType == 1):
            # straight + right turn
            self.pieces['rightTurn'] = RegularRoad(False, gridRef)
        
        elif(self.switchType == 2):
            # straight + left turn
            self.pieces['leftTurn'] = RegularRoad(False, gridRef)   #As explained in RegularRoad class, it is cretaed as a right turn first.
            self.pieces['leftTurn'].setOrientation(1, False)        #Then rotate it one time and not update the rotationCount.
       
        elif(self.switchType == 3): 
            # straight + right turn + left turn
            self.pieces['rightTurn'] = RegularRoad(False, gridRef)
            self.pieces['leftTurn'] = RegularRoad(False, gridRef)
            self.pieces['leftTurn'].setOrientation(1, False)
        return

    def setPosition(self, row, col):
        self.row = row
        self.col = col
        return  

    def setCwRot(self): 
        # straightforward 90 degree rotation: S->W, W -> N and so on.
        self.enter = (self.enter + 1) % 4
        if(self.switchType == 1):
            self.pieces['rightTurn'].setOrientation(1)
            self.pieces['direct'].setOrientation(1)
        
        elif(self.switchType == 2):
            self.pieces['leftTurn'].setOrientation(1)
            self.pieces['direct'].setOrientation(1)
        
        else: #switchType is 3
            self.pieces['rightTurn'].setOrientation(1)
            self.pieces['direct'].setOrientation(1)
            self.pieces['leftTurn'].setOrientation(1)

        return

    def setOrientation(self, rotationAmount):
        # rotate 90 degrees CW, directly change dir variables.

        self.rotationCount = (self.rotationCount + rotationAmount) % 4
        
        for i in range(0, rotationAmount):
            self.setCwRot()
        return

    def switchState(self):
        # defined only for switch roads. Changes which piece is active.

        if(self.switchType == 1):
            # if the direct is the active one, make the rightTurn active, and vice verca.
            if(self.activePiece == self.pieces['direct']):
                self.activePiece = self.pieces['rightTurn']
            else:
                self.activePiece = self.pieces['direct']

        elif(self.switchType == 2):
            # if the direct is the active one, make the leftTurn active, and vice verca.
            if(self.activePiece == self.pieces['direct']):
                self.activePiece = self.pieces['leftTurn']
            else:
                self.activePiece = self.pieces['direct']

        elif(self.switchType == 3): 
            #change state in CW order starting with direct. direct->rightTurn->leftTurn->direct
            if(self.activePiece == self.pieces['direct']):
                self.activePiece = self.pieces['rightTurn']
            elif(self.activePiece == self.pieces['rightTurn']):
                self.activePiece = self.pieces['leftTurn']
            else:
                self.activePiece = self.pieces['direct']
        return

    def getDuration(self, entdir):
         # add switch delay to default duration of the active piece
        
        return self.activePiece.getDuration(entdir) + self.switchDelay
        
    def getStop(self, entdir):
        # Train does NOT stop on this cell.
        return self.activePiece.getStop(entdir) 
        
    def nextCell(self,entdir):
        # if on the edge cells, and dir is outward, train will disappear
        # use activePiece to decide on exit direction if any
       
       # if the entrance is default direction, set exitDir according to active piece
       # else, if the entrance is one of the NotSwitched directions, treat it as a RegularRoad.
        if(entdir == self.enter):
            self.exitDir = None
            if(self.activePiece.dir1 == entdir):
                self.exitDir = self.activePiece.dir2
            elif(self.activePiece.dir2 == entdir):
                self.exitDir = self.activePiece.dir1
            else:
                print("invalid entry direction for this cell.")
                return None
        else:
            self.exitDir = self.enter
            
        #According to exitDir, if the nextCell is not out of bounds, return the nextCell
        if(self.exitDir == NORTH and self.myGrid.isOutOfBounds(self.row-1, self.col) == False):
        #     # row-1, col unchanged
            return(self.myGrid.grid[self.row-1][self.col] )
        elif(self.exitDir == SOUTH and self.myGrid.isOutOfBounds(self.row+1, self.col) == False):
        #     # row+1, col unchanged
            return(self.myGrid.grid[self.row+1][self.col])
        elif(self.exitDir == WEST and self.myGrid.isOutOfBounds(self.row, self.col-1) == False):
        #     #  col-1, row unchanged
            return(self.myGrid.grid[self.row][self.col-1])
        elif(self.exitDir == EAST and self.myGrid.isOutOfBounds(self.row, self.col+1) == False):
        #     #  col+1, row unchanged
            return(self.myGrid.grid[self.row][self.col+1])            
        else: #no available cell is found
            return None

    def getView(self):
        return self.visuals

    def getPos(self):
        return self.row, self.col
        
    def canEnter(self, entdir):
        #check the availability / connectivity of nextcell
        canEnter = False
        res = self.activePiece.canEnter(entdir)
        canEnter = canEnter or res

        return canEnter

class LevelCrossing(CellElement):
    # if all are in the '+' shape as shown in pdf, then rotation does not matter for these tiles.
    def __init__(self, gridRef):
        self.visuals = '+'
        self.rotationCount = 0
        self.myGrid = gridRef
        self.row = -1
        self.col = -1

        # has all 4 directions.
        # always exit entdir+2 in mod 4. So, no need the assign directions.
        return

    def setPosition(self, row, col):
        self.row = row
        self.col = col
        return    

    def setOrientation(self, rotationAmount, incrRot : bool = True):
        # since rotation does not make sense, just incrementing the rotationCount is enough.
        if(incrRot):
            self.rotationCount = (self.rotationCount + rotationAmount) % 4
        return

    def getDuration(self, entdir):
        return 1

    def getStop(self, entdir):
        # return 0(no waiting) if no other train parts are at this cell
        # if any trains, calculate upper bound on how long we should wait for them. possible deadlock here
        # fro Phase1, 0 is enough. Remaining will be impleneted in later phases.
        return 0

    def nextCell(self,entdir):
        # if on the edge cells, and dir is outward, train will disappear
        # calculate exit direction of the cell using dir value.

        # has all 4 directions. always exit entdir+2 in mod 4.
        self.exitDir = (entdir + 2) % 4

        #According to exitDir, if the nextCell is not out of bounds, return the nextCell
        if(self.exitDir == NORTH and self.myGrid.isOutOfBounds(self.row-1, self.col) == False):
        #     # row-1, col unchanged
            return(self.myGrid.grid[self.row-1][self.col] )
        elif(self.exitDir == SOUTH and self.myGrid.isOutOfBounds(self.row+1, self.col) == False):
        #     # row+1, col unchanged
            return(self.myGrid.grid[self.row+1][self.col])
        elif(self.exitDir == WEST and self.myGrid.isOutOfBounds(self.row, self.col-1) == False):
        #     #  col-1, row unchanged
            return(self.myGrid.grid[self.row][self.col-1])
        elif(self.exitDir == EAST and self.myGrid.isOutOfBounds(self.row, self.col+1) == False):
        #     #  col+1, row unchanged
            return(self.myGrid.grid[self.row][self.col+1])            
        else: #no available cell is found
            return None

    def getPos(self):
        return self.row, self.col

    def getView(self):
        return  self.visuals

    def canEnter(self, entdir):
        # has all 4 directions. can always enter EXCEPT when there is another train here.
        if(self.myGrid.hasTrain(self.row, self.col)):
            return False
        else:
            return True
    
class BridgeCrossing(CellElement):
    # if all are in the '+' shape as shown in pdf, then rotation does not matter for these tiles on phase1.
    def __init__(self, gridRef):
        self.visuals = '\u03A9' #visual is the omega sign
        self.rotationCount = 0
        self.myGrid = gridRef
        self.row = -1
        self.col = -1

        # Bridge is on West-East road segment as default.
        # other regular road dir can be deduced from these two.
        self.bridgeDir1 = WEST
        self.bridgeDir2 = EAST

        # all 4 directions always exit entdir+2 in mod 4.
        return

    def setPosition(self, row, col):
        self.row = row
        self.col = col
        return    

    def setCwRot(self):
        self.bridgeDir1 = (self.bridgeDir1 + 1) % 4
        self.bridgeDir2 = (self.bridgeDir2 + 1) % 4
        return

    def setOrientation(self, rotationAmount, incrRot : bool = True):
        #rotation makes sense here, we change the bridge's segment.
        if(incrRot):
            self.rotationCount = (self.rotationCount + rotationAmount) % 4  
        for i in range(0, rotationAmount):
            self.setCwRot()
        return

    def getDuration(self, entdir):
        return 1

    def getStop(self, entdir):
        return 0
        
    def nextCell(self,entdir):
        # if on the edge cells, and dir is outward, train will disappear
        # calculate exit direction of the cell using dir value.

        # has all 4 directions. always exit entdir+2 in mod 4.
        self.exitDir = (entdir + 2) % 4

        #According to exitDir, if the nextCell is not out of bounds, return the nextCell
        if(self.exitDir == NORTH and self.myGrid.isOutOfBounds(self.row-1, self.col) == False):
        #     # row-1, col unchanged
            return(self.myGrid.grid[self.row-1][self.col] )
        elif(self.exitDir == SOUTH and self.myGrid.isOutOfBounds(self.row+1, self.col) == False):
        #     # row+1, col unchanged
            return(self.myGrid.grid[self.row+1][self.col])
        elif(self.exitDir == WEST and self.myGrid.isOutOfBounds(self.row, self.col-1) == False):
        #     #  col-1, row unchanged
            return(self.myGrid.grid[self.row][self.col-1])
        elif(self.exitDir == EAST and self.myGrid.isOutOfBounds(self.row, self.col+1) == False):
        #     #  col+1, row unchanged
            return(self.myGrid.grid[self.row][self.col+1])            
        else: #no available cell is found
            return None

    def getPos(self):
        return self.row, self.col

    def getView(self):
        return  self.visuals

    def canEnter(self, entdir):
        # has all 4 directions. can always enter since bridge prevents from a collision.
        return True

class Station(CellElement):
    #It is just like a straight regularRoad, but for simplcity we don't create it using RegularRoad class. 
    def __init__(self, gridRef): 
        self.visuals = '\u0394' #the visual is the delta sign.
        self.rotationCount = 0
        self.myGrid = gridRef
        self.row = -1
        self.col = -1
        #default dir values
        self.dir1 = SOUTH
        self.dir2 = NORTH
        return

    def setPosition(self, row, col):
        self.row = row
        self.col=  col
        return  

    def setCwRot(self):
        self.dir1 = (self.dir1 + 1) % 4
        self.dir2 = (self.dir2 + 1) % 4
        return

    def setOrientation(self, rotationAmount, incrRot : bool = True):
        #like a straight road, increment rotationcount and rotate the directions rotationAmount times.
        if(incrRot):
            self.rotationCount = (self.rotationCount + rotationAmount) % 4
        for i in range(0, rotationAmount):
            self.setCwRot()
        return

    def switchState(self):
        return

    def getDuration(self, entdir): #since it will be stopped in station, add the deault value to the stop value. 
        return 1 + self.getStop(entdir)

    def getStop(self, entdir):
        return 3

    def nextCell(self,entdir):
        # if on the edge cells, and dir is outward, train will disappear
        # calculate exit direction of the cell using dir value.

        self.exitDir = None
        if(self.dir1 == entdir):
            self.exitDir = self.dir2
        elif self.dir2 == entdir:
            self.exitDir = self.dir1
        else:
            return None

        #According to exitDir, if the nextCell is not out of bounds, return the nextCell
        if(self.exitDir == NORTH and self.myGrid.isOutOfBounds(self.row-1, self.col) == False):
        #     # row-1, col unchanged
            return(self.myGrid.grid[self.row-1][self.col] )
        elif(self.exitDir == SOUTH and self.myGrid.isOutOfBounds(self.row+1, self.col) == False):
        #     # row+1, col unchanged
            return(self.myGrid.grid[self.row+1][self.col])
        elif(self.exitDir == WEST and self.myGrid.isOutOfBounds(self.row, self.col-1) == False):
        #     #  col-1, row unchanged
            return(self.myGrid.grid[self.row][self.col-1])
        elif(self.exitDir == EAST and self.myGrid.isOutOfBounds(self.row, self.col+1) == False):
        #     #  col+1, row unchanged
            return(self.myGrid.grid[self.row][self.col+1])            
        else: #no available cell is found
            return None

    def getPos(self):
        return self.row, self.col

    def getView(self):
        return  self.visuals

    def canEnter(self, entdir):
        #check the availability / connectivity of nextcell
        return (self.dir1 == entdir or self.dir2 == entdir)

class Train():
    #GameGrid takes care of the created trains and their effcts in the grid view.
    def __init__(self, nWagons, cell : CellElement, gridRef : GameGrid):
        self.wagonCount = nWagons
        self.totalLength = nWagons+1 # cars + train engine
        self.currCell = cell
        self.wagonCountPerCell = 2 # effectively, each 'car' takes 1/2 of a cell.
        self.gridRef = gridRef      # ref to GameGrid to be in communication.
        self.coveredCellCount = math.ceil(self.totalLength / self.wagonCountPerCell) 
        self.trainSpeed = 0.5
        # one of: "moving", "movingReverse", "stopped"
        self.status = "stopped" 
        self.enginePosRow, self.enginePosCol = cell.getPos()
        
        self.destReached = False # reset each time state changes from moving
        self.currMoveTime = 0 # reset each time state changes from 'moving'
        self.currStopTime = 0 # reset each time state changes from 'stopped'
        self.entDir = NORTH
        self.exitDir = SOUTH # meaning move from north to south in current cell.
        return
    
    def enterCell(self, nextCell : CellElement, entdir):
        #it locates the train in a given cell position using entdir value.
        self.entDir = entdir
        self.enginePosRow, self.enginePosCol = nextCell.getPos()
        self.currCell = nextCell

    def getEnginePos(self):
        return self.enginePosRow, self.enginePosCol

    def getStatus(self): 
        return self.status
    
    def getGeometry(self):
        # Gets the geometry of the train path, engine and cars. 
        # Implemented in later phases where full train needs to be displayed on a curve during simulation
        return

    def moveToDest(self, moveTime):
        # calculate&set new engine pos after moving for moveTime
        self.currMoveTime += moveTime

        requiredTime = self.currCell.getDuration(self.entDir)
        requiredTime /= self.trainSpeed # so if speed = 2, it takes half the time to pass this cell. reverse deltax calc ;p
        
        remainingMoveTime = requiredTime - self.currMoveTime
        excessTime = -remainingMoveTime # use this time to wait for that duration.
        
        perct = self.currMoveTime / requiredTime
        if(perct >= 1):
            self.destReached = True

        startPosX,startPosY = self.currCell.getPos() # returns (row,col)
        endPosX, endPosY = self.destCell.getPos()

        newPosX = self.lerp(startPosX, endPosX, perct)
        newPosY = self.lerp(startPosY, endPosY, perct)

        self.enginePosRow = newPosX
        self.enginePosCol = newPosY
        print("train new pos:", self.enginePosRow, self.enginePosCol)
        return excessTime

    def lerp(self, start,end,t):
        return ((1-t)*start) + (t * end)
        
    def changeState(self, newState):
        self.currMoveTime = 0
        self.currStopTime = 0            
        self.destReached = False
        self.status = newState
        if(newState == 'moving'):

            nextCell = self.currCell.nextCell(self.entDir)
            if(nextCell != None):
                self.destCell = nextCell
                self.exitDir = self.currCell.exitDir
                self.nextEnterDir = (self.currCell.exitDir + 2) % 4
                print("entdir: ", self.entDir, "exitDir: ", self.exitDir, "nextEntDir; ", self.nextEnterDir)

            else:
                    # dead end or out of bounds. disappear for now.
                self.changeState('stopped')
                self.gridRef.trainDisappear(self)
                
        elif(newState == 'stopped'):
            self.currCell = self.destCell
            self.entDir = self.nextEnterDir
            self.exitDir = None
            self.nextEnterDir = None

    def tick(self):

        if(self.status == "moving"):
            # keep moving towards the destination for timeStep seconds.
            excessTime = self.moveToDest(self.gridRef.timeStep)  # calculates new pos after move
            if(self.destReached):
                self.changeState('stopped')
                # if(excessTime > 0): # use this time to wait.
                #     self.currStopTime += excessTime
        elif(self.status == "stopped"):

            self.currStopTime += self.gridRef.timeStep
            remainingWaitTime = self.currCell.getStop(self.entDir) - self.currStopTime
            moveTime = -remainingWaitTime # if remaining time > 0 then this one <0, so dont move.
            print("waiting")
            if(remainingWaitTime <= 0):
                self.changeState('moving')
                self.moveToDest(moveTime)
                if(self.destReached): # as a result of moveToDest, this might change.
                    self.changeState('stopped')
        return 1
    
    