background = '0'
NORTH = 0
EAST = 1
SOUTH = 2
WEST = 3

dirs = {0 : "NORTH", 1 : "EAST", 2 : "SOUTH", 3 : "WEST"}
class CellElement():

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
    def setNextCWRotation(self):
        return   
    def getView():
        return

    # Additional Interface methods
    def canEnter(self, entdir):
        return
    def getPos(self):
        return

class GameGrid():
    
    def __init__ (self, row, col):
        self.row = row
        self.col = col
        self.grid = []
        self.view = []
        
        # Train refs to draw them on screen, on top of tile view.
        self.activeTrains = []
        for i in range(0, row):
            self.grid.append([])
            self.view.append([])
            for j in range(0, col):
                c = RegularRoad(True, self.grid)
                c.visuals = '_'
                c.setPosition(i,j)
                self.grid[i].append(c)
                self.view[i].append(c.visuals)


    def addElement(self, cellElm, row, col):
        cellElm.setPosition(row, col)
        self.grid[row][col] = cellElm
        self.view[row][col] = cellElm.visuals
        return

    def removeElement(self, row, col):
        empty = RegularRoad(True, self.grid)
        empty.visuals = '_'
        self.grid[row][col] = empty
        self.view[row][col] = '_' #display for BG
        return

    def display(self):
        for i in range(0,self.row):
            for j in range(0, self.col):
                print(self.view[i][j], end=' ')
            print('\n')

    def isOutOfBounds(self, i, j):
        if(i >= self.row or j >= self.col or i < 0 or j < 0): 
            return True
        return False

    def updateView(self):
        return

    def startSimulation(self): 
        return

    def setPauseResume(self):
        return

    def stopSimulation(self):
        return
    
    def spawnTrain(self, wagonCount, row, col):

        if(self.isOutOfBounds(row,col)):
            print("invalid spawn pos for train.", row, col)
            return
        
        spawnCell = self.grid[row][col]
        t = Train(wagonCount, spawnCell, self)
        self.registerTrain(t)
        self.drawTrains()
        return t

    def registerTrain(self, train):
        self.activeTrains.append(train)
        return

    def trainDisappear(self,train):
        self.activeTrains.remove(train)
        return

    def drawTrains(self):
        for t in self.activeTrains:
            self.view[t.enginePosRow][t.enginePosCol] = 't'
        return
        
    def updateTrainDisplay(self, train, prevRow, prevCol):
        # use train's pos & path data to draw it in proper place, on top of the tiles.

        # train exited this tile, redraw the tile visuals there
        self.view[prevRow][prevCol] = self.grid[prevRow][prevCol].visuals
        self.drawTrains()
        return

    # Used to check for collisions/waiting by the cells.
    def hasTrain(self, row, col):
        for t in self.activeTrains:
            if(t.enginePosRow == row and t.enginePosCol == col):
                 return True
        return False



class RegularRoad(CellElement):
    def __init__(self, isStraight, gridRef):
        self.visuals = '_'
        self.rotationCount = 0
        self.myGrid = gridRef
        self.row = -1
        self.col = -1
        self.isRegular = isStraight
        if(isStraight):
            self.dir1 = SOUTH
            self.dir2 = NORTH
            self.visuals = '|'
        else: # default is a Right turn as in the pdf.
            # rotate this one time CW to get a left turn if needed
            self.visuals = 'R'
            self.dir1 = SOUTH
            self.dir2 = EAST
        return
    def makeLeftTurn(self):
        self.visuals = 'L'
        self.rotationCount = 0
        self.setOrientation( 1, False)
        return self

    def setPosition(self, row, col):
        self.row = row
        self.col = col
        return    
    def setCwRot(self):
        self.dir1 = (self.dir1 + 1) % 4
        self.dir2 = (self.dir2 + 1) % 4
        return

    def setOrientation(self, rotationAmount, incrRot : bool = True):
        if(incrRot):
            self.rotationCount = (self.rotationCount + rotationAmount) % 4
        for i in range(0, rotationAmount):
            self.setCwRot()
        return


    def switchState(self):
        return
    def getDuration(self, entdir):
        return
    def getStop(self, entdir):
        return

    def nextCell(self,entdir):
        # if on the edge cells, and dir is outward, train will disappear
        # calculate exit direction of the cell using dir value.
        # connection check for next cell is missing DO IT

        self.exitDir = None
        if(self.dir1 == entdir):
            self.exitDir = self.dir2
        elif self.dir2 == entdir:
            self.exitDir = self.dir1
        else:
            return None

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
        return (self.dir1 == entdir or self.dir2 == entdir)



class SwitchRoad(CellElement):
    def __init__(self, typeofSwitch, gridRef):
        # create 'pieces' of the switch.
        self.visuals = 'S'
        self.myGrid = gridRef
        self.rotationCount = 0
        self.switchType = typeofSwitch
        self.pieces = {'direct' : RegularRoad(True, gridRef)}
        self.activePiece = self.pieces['direct']
        self.enter = SOUTH #default switch location is south for all type of switches
        self.switchDelay = 2
        
        if(self.switchType == 1):
            # straight + right turn
            self.pieces['rightTurn'] = RegularRoad(False, gridRef)
        
        elif(self.switchType == 2):
            # straight + left turn
            self.pieces['leftTurn'] = RegularRoad(False, gridRef)
            self.pieces['leftTurn'].setOrientation(1, False)
       
        elif(self.switchType == 3): 
            # straight + left turn + right turn
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
        # only for switch roads. change which piece is active.

        if(self.switchType == 1):
            # if right make direct, if direct make right
            if(self.activePiece == self.pieces['direct']):
                self.activePiece = self.pieces['rightTurn']
            else:
                self.activePiece = self.pieces['direct']

        elif(self.switchType == 2):
            #if left make direct, if direct make left
            if(self.activePiece == self.pieces['direct']):
                self.activePiece = self.pieces['leftTurn']
            else:
                self.activePiece = self.pieces['direct']

        elif(self.switchType == 3): 
            if(self.activePiece == self.pieces['direct']):
                self.activePiece = self.pieces['rightTurn']
            elif(self.activePiece == self.pieces['rightTurn']):
                self.activePiece = self.pieces['leftTurn']
            else:
                self.activePiece = self.pieces['direct']
        return

    def getDuration(self, entdir):
        # It takes one second to pass this cell.
        # add switch delay to default duration of the activepiece
        
        return self.activePiece.getDuration() + self.switchDelay
        

    def getStop(self, entdir):
        # Train does NOT stop on this cell.
        return self.activePiece.getStop() 
        
    def nextCell(self,entdir):
        # if on the edge cells, and dir is outward, train will disappear
        # use activePiece to decide on exit direction if any
       
        if(entdir == self.enter):
            self.exitDir = None
            if(self.activePiece.dir1 == entdir):
                self.exitDir = self.activePiece.dir2
            elif self.activePiece.dir2 == entdir:
                self.exitDir = self.activePiece.dir1
            else:
                print("invalid entry direction for this cell.")
                return None
        else:
            self.exitDir = self.enter
            
        
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
        return self.activePiece.visuals

    def getPos(self):
        return self.row, self.col
        
    def canEnter(self, entdir):
        canEnter = False
        for i in self.pieces.keys:
            res = self.pieces[i].canEnter(entdir)
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
        # always exit entdir+2 in mod 4.
        return

    def setPosition(self, row, col):
        self.row= row
        self.col = col
        return    

    def setOrientation(self, rotationAmount, incrRot : bool = True):
        if(incrRot):
            self.rotationCount = (self.rotationCount + rotationAmount) % 4
        # for i in range(0, rotationAmount):
        #     self.setCwRot()
        return

    def getDuration(self, entdir):
        return 1

    def getStop(self, entdir):
        # return 0(no waiting) if no other train parts are at this cell
        # if any trains, calculate upper bound on how long we should wait for them. possible deadlock here :D?
        if(self.myGrid.hasTrain(self.row, self.col)):
            return 3 # TODO use that trains length and pos to calculate this.
        else:
            return 0
        
    def nextCell(self,entdir):
        # if on the edge cells, and dir is outward, train will disappear
        # calculate exit direction of the cell using dir value.

        # has all 4 directions. always exit entdir+2 in mod 4.
        self.exitDir = (entdir + 2) % 4

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
    # if all are in the '+' shape as shown in pdf, then rotation does not matter for these tiles.
    def __init__(self, gridRef):
        self.visuals = '\u03A9'
        self.rotationCount = 0
        self.myGrid = gridRef
        self.row = -1
        self.col = -1

        # Bridge is on West-East road segment.
        # other regular road dir can be deduced from these two.
        self.bridgeDir1 = WEST
        self.bridgeDir2 = EAST

        # has all 4 directions always exit entdir+2 in mod 4.
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
        if(incrRot):
            self.rotationCount = (self.rotationCount + rotationAmount) % 4
        for i in range(0, rotationAmount):
            self.setCwRot()
        return

    def getDuration(self, entdir):
        return 1

    def getStop(self, entdir):
        # return 0(no waiting) if no other train parts are at this cell
        # if any trains, calculate upper bound on how long we should wait for them. possible deadlock here :D?
        if(self.myGrid.hasTrain(self.row, self.col)):
            return 3 # TODO use that trains length and pos to calculate this.
        else:
            return 0
        

    def nextCell(self,entdir):
        # if on the edge cells, and dir is outward, train will disappear
        # calculate exit direction of the cell using dir value.

        # has all 4 directions. always exit entdir+2 in mod 4.
        self.exitDir = (entdir + 2) % 4

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
        return True
class Station(CellElement):
    def __init__(self, gridRef):
        self.visuals = '\u0394'
        self.rotationCount = 0
        self.myGrid = gridRef
        self.row = -1
        self.col = -1

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
        if(incrRot):
            self.rotationCount = (self.rotationCount + rotationAmount) % 4
        for i in range(0, rotationAmount):
            self.setCwRot()
        return

    def switchState(self):
        return
    def getDuration(self, entdir):
        return 1 + self.getStop(entdir)
    def getStop(self, entdir):
        return 5

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
        return (self.dir1 == entdir or self.dir2 == entdir)
    # There are two options to introduce trains in the simulation: Adding trains in
# the Grid with appropriate methods, or adding train parks that dynamically add
# trains during simulation

# TODO Open question:
# who displays the train?
# Grid: then train should register with the grid and call updateDisplay() each time its pos change(during sim)

# TODO: a Game manager/controller class (think main()), which creates & setups the grid, runs the simulation, gets train pos updates and commands Grid to draw properly.
# thats probably the best way.
import math
class Train():
    def __init__(self, nWagons, cell : CellElement, gridRef : GameGrid):
        self.wagonCount = nWagons
        self.totalLength = nWagons+1 # cars + train engine
        self.currCell = cell
        self.wagonCountPerCell = 2 # effectively, each 'car' takes 1/2 of a cell.
        self.gridRef = gridRef
        self.coveredCellCount = math.ceil(self.totalLength / self.wagonCountPerCell)

        # one of: "moving", "movingReverse", "stopped"
        self.status = "stopped" 
        self.enginePosRow, self.enginePosCol = cell.getPos()
        # self.updateDisplay() # Since grid creates the trains, this is unnecessary at the moment
        return
    
    def enterCell(self, nextCell : CellElement):

        if(nextCell is None):
            self.gridRef.trainDisappear(self)
        else:
            # update pos
            self.currCell = nextCell
            self.enginePosRow, self.enginePosCol = nextCell.getPos()
            self.updateDisplay()
        return
    
    def getEnginePos(self):
        return self.enginePosRow, self.enginePosCol

    def getStatus(self):
        return self.status
    
    def getGeometry(self):
        # Gets the geometry of the train path, engine and cars. 
        # Implemented in later phases where full train needs to be displayed on a curve during simulation

        # TODO
        # how to know where the train wagons are?
        # we know train engine is at the cell nextCell when enterCell is called.
        # the rest of the train wagons' positions should computed somehow.
        # do we keep track of the past (2-3) cells that the train have been in?
        # creating & showing a path for the whole train needs more work.

        return

    def updateDisplay(self,prevRow, prevCol):
        # notify grid/game manager class with new pos?
        self.gridRef.updateTrainDisplay(self, prevRow, prevCol)
        return

        
    def tempMove(self, rowDelta, colDelta):
        self.prevRow, self.prevCol = self.enginePosRow, self.enginePosCol
        self.enginePosRow += rowDelta
        self.enginePosCol += colDelta
        self.updateDisplay(self.prevRow, self.prevCol)
    