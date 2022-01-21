from socket import *
from threading import *
import os,stat
import trainLib as lib
import pickle
import sqlite3
import time

# allgrids = {}
# allgridslock = Lock()

# gridlocks = {} # dict: key: gridname value: lock
# gridlockslock = Lock()

gridobservers = {}
obslock = Lock()
# add grid when its created
# key: gridname, value: list of GridObservers 
class GridObserver():
    def __init__(self, sock: socket):
        self.sock = sock
        return
    def simNotification(self, state):
        # send updated grid.view
        self.sock.send(state.encode())
        print('observer sent received state to client')
        return

    def updateNotification(self, msg):
        print('observer received updated notf:',  )  
        self.sock.send(msg)

class GridWrapper():
    def __init__(self, grid, gridname):
        self.grid = grid
        self.gridname = gridname
        self.userlist = []
        self.isShared = False

    # def createlock(self):
    #     global gridlocks
    #     with gridlockslock:
    #         gridlocks[self.gridname] = Lock()

def simulator():
    con = sqlite3.connect('trainsim.db')
    cursor = con.cursor()
    timestep = 1
    while(1):
        # load all Grids from DB
        # Run sim for all of them.
        # notify their observers
        #print("simulating one frame")
        query = "SELECT * FROM grid"
        cursor.execute(query)
        result = cursor.fetchall()
        for griddata in result:
            gridname = griddata[0]
            data = griddata[1]
            grid = pickle.loads(data)

            if(grid.isRunning and (not grid.isPaused)):
                #print("advance sim on grid, from simualtor")
                grid.advanceSim()
                with obslock:
                    itsobservers = gridobservers[gridname]
                    for observer in itsobservers:
                        #print("notify observer?")
                        map = grid.getdisplayable() +' \n'
                        trainPositions = grid.getTrainPositions() # return list of list of tuples[(x,y), (x2,y2)]
                        trainInfo = ""
                        for pos in trainPositions:
                            i = 0
                            for wagonPos in pos:
                                if(i == 0):
                                    trainInfo +=  "Engine pos row: " + str(wagonPos[0]) + " col: " + str(wagonPos[1]) + '\n'
                                else:
                                    trainInfo +=  "wagon " + str(i) + " pos row: " + str(wagonPos[0]) + " col: " + str(wagonPos[1]) + '\n'
                                i+=1
                                
                        msg = map + trainInfo
                        observer.simNotification(msg)

                pickled  = pickle.dumps(grid)
                query = "UPDATE grid SET data = ? WHERE gridname = ?"
                cursor.execute(query,(pickled,gridname))
            #else:
                #print("grid is not running: " + gridname)

        con.commit()
        time.sleep(timestep)
    return
def worker(sock : socket):
    
    global allgridslock, allgrids, gridlocks, gridlockslock
    global gridobservers
    # serves client with username user1
    # each worker should now the username of the connected client. username will be used in lib calls

    # username of the user currently logged in
    username = ''
    isLoggedIn = False

    myobserver = GridObserver(sock)
    con = sqlite3.connect('trainsim.db')

    # later, this is modified as the result of attach gridname command
    attachedGridName = "default"

    while True:
        error = 'ERROR'.encode()
        space = ' '.encode()
        msg = sock.recv(4096)
        # parse msg
        #m = msg.decode()
        #m = m + " received."
        args = msg.split()
        command = args[0]
        command = command.decode()
        if (True):
            if command == 'create': # CREATE row col gridname
                if(isLoggedIn):
                    msg = 'GRID CREATED'.encode()
                    row = int(args[1].decode())
                    col = int(args[2].decode())
                    gridname = args[3].decode()

                    creategrid(row,col,gridname, username, con)

                    with obslock:
                        gridobservers[gridname] = [] # empty list of observer
                    sock.send(args[1]+ 'x'.encode()+args[2]+space+msg+' AS '.encode()+gridname.encode())
                else:
                    sock.send("Please login first.".encode())

            elif command == "login": # LOGIN username password                
                enteredusername = args[1].decode()
                enteredpassword = args[2].decode()

                cursor = con.cursor()
                query = "SELECT password FROM user WHERE username = ?"
                cursor.execute(query, (enteredusername,))
                result = cursor.fetchone()
                if(result != None and result[0] == enteredpassword):
                    sock.send("HELLO ".encode() + args[1])
                    isLoggedIn = True
                    username = enteredusername # update currently logged in username
                else:
                    sock.send("Wrong username or password. ".encode())
                    isLoggedIn = False
                con.commit()

            elif command == 'attach':
                # ATTACH gridname
                gridname = args[1].decode()

                cursor = con.cursor()
                query = "SELECT userlist,author FROM grid WHERE gridname = ?"
                cursor.execute(query, (gridname,))

                result = cursor.fetchone()
                if(result is None):
                    sock.send('Grid not found.'.encode())
                    
                userlist = pickle.loads(result[0])

                authorized = False
                for usr in userlist:
                    if(usr == username):
                        authorized= True
                        break
                if(not authorized):
                    sock.send("Not authorized to attach this grid.".encode())
                
                else:
                    attachedGridName = gridname
                    with obslock:
                        gridobservers[attachedGridName].append(myobserver)
                        print("ATTACHED " + username + " TO OBSERVER LIST.")

                    cursor = con.cursor()
                    query = "UPDATE user SET gridname = ? WHERE username = ?"
                    cursor.execute(query, (attachedGridName, username))
                    con.commit()
                    sock.send('Attached to grid: '.encode() + args[1])

            elif command == 'detach':
                # detach previously attached grid

                # local, only to be able to send in the response message.
                attachedGridNameCache = attachedGridName
                with obslock:
                    gridobservers[attachedGridName].remove(myobserver)
                    print("Detached " + username + " from grid: " + attachedGridName)
                
                attachedGridName = None
                cursor = con.cursor()
                query = "UPDATE user SET gridname = ? WHERE username = ?"
                cursor.execute(query, (None, username))
                con.commit()
                sock.send('Detached from grid: '.encode() + attachedGridNameCache.encode())

            elif command == 'share':
                #usage: share gridname
                gridname = args[1].decode()

                cursor = con.cursor()
                query = "SELECT userlist,author FROM grid WHERE gridname = ?"
                cursor.execute(query, (gridname,))
                result = cursor.fetchone()
                
                userlist = pickle.loads(result[0])
                author = result[1]
                if(author == username):
                    # only the author/creator of a grid can share/unshare it.
                    # add all users to userlist(users that can access this grid) of this grid.

                    query = "SELECT username FROM user WHERE username != ?"
                    cursor.execute(query, (username,))
                    # get all other users
                    otherusers = cursor.fetchall()
                    for usr in otherusers:
                        userlist.append(usr[0])

                    # Write back the updated list
                    pickleduserlist = pickle.dumps(userlist)
                    query = "UPDATE grid SET userlist = ? WHERE gridname = ?"
                    cursor.execute(query, (pickleduserlist, gridname))
                    con.commit() 
                    sock.send(("You shared grid: " + gridname + " with other users.").encode())
                else:
                    sock.send('You are authorized to share this grid.'.encode())

            elif command == 'unshare':
                #usage: share gridname
                gridname = args[1].decode()

                cursor = con.cursor()
                query = "SELECT userlist,author FROM grid WHERE gridname = ?"
                cursor.execute(query, (gridname,))
                result = cursor.fetchone()
                
                author = result[1]
                if(author == username):
                    # only the author/creator of a grid can share/unshare it.
                    # Remove all others users from the userlist, only author remains.
                    userlist = [author]
                    
                    # Write back the updated list
                    pickleduserlist = pickle.dumps(userlist)
                    query = "UPDATE grid SET userlist = ? WHERE gridname = ?"
                    cursor.execute(query, (pickleduserlist, gridname))
                    con.commit() 
                    sock.send(("You unshared grid: " + gridname + " with other users.").encode())
                else:
                    sock.send('You are authorized to unshare this grid.'.encode())

            elif command == 'duplicate':
                #usage: duplicate gridname newgridname
                gridname = args[1].decode()
                newgridname = args[2].decode()
                # duplicate grid with gridname, if that grid is accessable by this user.
             
                cursor = con.cursor()
                query = "SELECT gridname,data,userlist FROM grid"
                cursor.execute(query)
                result = cursor.fetchall()

                for grid in result:
                    storedgridname = grid[0]
                    if(storedgridname == gridname):
                        userlist = pickle.loads(grid[2])
                        canSee = False
                        for usr in userlist:
                            if(usr == username):
                                canSee = True
                        if(canSee):
                            # then duplicate    
                            with obslock: # empty list of observers for now.
                                gridobservers[newgridname] = [] 

                            query = "INSERT INTO grid (gridname,data, userlist, author) VALUES (?, ?, ?, ?)"
                            newuserlist = [username] # we are author now
                            pickledlist = pickle.dumps(newuserlist)
                            cursor.execute(query, (newgridname, grid[1], pickledlist, username))
                            con.commit()
                            sock.send(("You have duplicated the grid " + gridname + " created new grid with name: " + newgridname).encode())
                        else:
                            sock.send("You are not authorized to duplicated this grid.".encode())
            elif command == 'logout':
                # Client should login afterwards to be able use any of the functionality.
                if(isLoggedIn):
                    isLoggedIn = False
                    username = ''
                    sock.send("Logged out.".encode())
                else:
                    sock.send("Error, you were not logged in.".encode())

            elif command == 'delete': #delete gridname , it should be deleted if attached
                gridname = args[1].decode()

                cursor = con.cursor()
                query = "DELETE FROM TABLE grid WHERE gridname = ?"
                cursor.execute(query, (gridname,))
                con.commit()

                msg = ('Deleted grid '+gridname).encode()
                with obslock:
                    itsobservers = gridobservers[gridname]
                    for observer in itsobservers:
                        observer.updateNotification(msg)
                # sock.send(msg)

            elif command == 'listall':
                 #list grids that are accessable by this user.
                 # Accessable ones: ones that are shared with, and/or created by this user.
                
                cursor = con.cursor()
                query = "SELECT gridname,userlist FROM grid"
                cursor.execute(query)
                result = cursor.fetchall()

                response = "All available grids: "
                for griddata in result:
                    gridname = griddata[0]
                    userlist = pickle.loads(griddata[1])

                    canSee = False
                    for usr in userlist:
                        if(usr == username):
                            canSee = True
                            response = response + gridname + ","
                    
                con.commit()
                sock.send(response.encode())

            elif command == 'add': #add type row col
                type = args[1].decode()
                row = int(args[2].decode())
                col = int(args[3].decode())
                msg = 'TYPE ELEMENT ADDED AT'.encode()

                cursor = con.cursor()
                query = "SELECT data FROM grid WHERE gridname = ?"
                cursor.execute(query,(attachedGridName,))
                result = cursor.fetchone()
                grid = pickle.loads(result[0])

                grid.addElement(getnewelem(type, grid), row, col)

                pickled = pickle.dumps(grid)

                query = "UPDATE grid SET data = ? WHERE gridname = ?"
                cursor.execute(query, (pickled, attachedGridName))
                con.commit()
                
                msg = ("Added element. new grid:\n" + grid.getdisplayable()).encode()
                # Notify all observer clients
                with obslock:
                    itsobservers = gridobservers[gridname]
                    for observer in itsobservers:
                        observer.updateNotification(msg)

            elif command == 'remove': #remove row col
                row = int(args[1].decode())
                col = int(args[2].decode())
                msg = 'ELEMENT REMOVED AT '.encode()

                cursor = con.cursor()
                query = "SELECT data FROM grid WHERE gridname = ?"
                cursor.execute(query,(attachedGridName,))
                result = cursor.fetchone()
                grid = pickle.loads(result[0])

                grid.removeElement(row, col)
                pickled = pickle.dumps(grid)

                query = "UPDATE grid SET data = ? WHERE gridname = ?"
                cursor.execute(query, (pickled, attachedGridName))
                con.commit()

                msg = ("Removed element. new grid:\n" + grid.getdisplayable()).encode()
                # Notify all observer clients
                with obslock:
                    itsobservers = gridobservers[gridname]
                    for observer in itsobservers:
                        observer.updateNotification(msg)

            elif command == 'chstate': #chstate row col
                row = int(args[1].decode())
                col = int(args[2].decode())
                msg = 'STATE OF THE SWITCH AT'.encode()
                msg2 = 'CHANGED'.encode()

                cursor = con.cursor()
                query = "SELECT data FROM grid WHERE gridname = ?"
                cursor.execute(query,(attachedGridName,))
                result = cursor.fetchone()
                grid = pickle.loads(result[0])

                cell = grid.grid[row][col]
                cell.switchState()
                pickled = pickle.dumps(grid)

                query = "UPDATE grid SET data = ? WHERE gridname = ?"
                cursor.execute(query, (pickled, attachedGridName))
                con.commit()

                msg = ("Changed switch state.".encode())
                # Notify all observer clients
                with obslock:
                    itsobservers = gridobservers[gridname]
                    for observer in itsobservers:
                        observer.updateNotification(msg)
            
            elif command == 'rotate':  #rotate times row col
                times = int(args[1].decode())
                row = int(args[2].decode())
                col = int(args[3].decode())
                msg = 'ELEMENT AT'.encode()
                msg2 = 'ROTATED'.encode()
                msg3 = 'TIMES'.encode()
                
                cursor = con.cursor()
                query = "SELECT data FROM grid WHERE gridname = ?"
                cursor.execute(query,(attachedGridName,))
                result = cursor.fetchone()
                grid = pickle.loads(result[0])

                cell = grid.grid[row][col]
                cell.setOrientation(times)
                print(cell.rotationCount)
                pickled = pickle.dumps(grid)

                query = "UPDATE grid SET data = ? WHERE gridname = ?"
                cursor.execute(query, (pickled, attachedGridName))
                con.commit()

                msg = ("Rotated. new grid:\n" + grid.getdisplayable()).encode()
                # Notify all observer clients
                with obslock:
                    itsobservers = gridobservers[gridname]
                    for observer in itsobservers:
                        observer.updateNotification(msg)
                # sock.send(msg + space + args[2] + space + args[3] + space + msg2 + space + args[1] + msg3)
                # Notify client

            elif command == 'start':  #startsim
                msg='SIMULATION STARTED'.encode()

                cursor = con.cursor()
                query = "SELECT data FROM grid WHERE gridname = ?"
                cursor.execute(query,(attachedGridName,))
                res = cursor.fetchone()
                grid = pickle.loads(res[0])
                grid.startSimulation()

                pickled = pickle.dumps(grid)

                query = "UPDATE grid SET data = ? WHERE gridname = ?"
                cursor.execute(query,(pickled, attachedGridName))
                con.commit()
                sock.send(msg)

            elif command == 'stop':
                msg='SIMULATION STOPPED'.encode()
                
                cursor = con.cursor()
                query = "SELECT data FROM grid WHERE gridname = ?"
                cursor.execute(query,(attachedGridName,))
                res = cursor.fetchone()
                grid = pickle.loads(res[0])
                grid.stopSimulation()

                pickled = pickle.dumps(grid)

                query = "UPDATE grid SET data = ? WHERE gridname = ?"
                cursor.execute(query,(pickled, attachedGridName))
                con.commit()

                msg = ("Simulation stopped.".encode())
                # Notify all observer clients
                with obslock:
                    itsobservers = gridobservers[gridname]
                    for observer in itsobservers:
                        observer.updateNotification(msg)

            elif command == 'pause':
                msg='SIMULATION PAUSED'.encode()

                cursor = con.cursor()
                query = "SELECT data FROM grid WHERE gridname = ?"
                cursor.execute(query,(attachedGridName,))
                res = cursor.fetchone()
                grid = pickle.loads(res[0])
                grid.pauseSimulation()

                pickled = pickle.dumps(grid)

                query = "UPDATE grid SET data = ? WHERE gridname = ?"
                cursor.execute(query,(pickled, attachedGridName))
                con.commit()

                # Notify all observer clients
                with obslock:
                    itsobservers = gridobservers[gridname]
                    for observer in itsobservers:
                        observer.updateNotification(msg)

            elif command == 'resume':
                msg='SIMULATION RESUMED'.encode()

                cursor = con.cursor()
                query = "SELECT data FROM grid WHERE gridname = ?"
                cursor.execute(query,(attachedGridName,))
                res = cursor.fetchone()
                grid = pickle.loads(res[0])
                grid.resumeSimulation()

                pickled = pickle.dumps(grid)

                query = "UPDATE grid SET data = ? WHERE gridname = ?"
                cursor.execute(query,(pickled, attachedGridName))
                con.commit()

                # Notify all observer clients
                with obslock:
                    itsobservers = gridobservers[gridname]
                    for observer in itsobservers:
                        observer.updateNotification(msg)

            elif command == 'bye':
                msg = 'BYE TO YOU'.encode()
                sock.send(msg)
                sock.close()
                break

            else:
                sock.send(error)

def getnewelem(typeStr, globalGrid):
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
    elif(typeStr == "trainshed"):
        newElm = lib.TrainShed(globalGrid)
    else:
        print("typeOfCell(string) argument is invalid. Abort.")
        return
    return newElm

def creategrid(row, col , gridname, username, con):

    # global allgridslock, allgrids
    cursor = con.cursor()
    rawgrid = lib.GameGrid(row, col)
    pickledgrid = pickle.dumps(rawgrid)

    query = "INSERT INTO grid (gridname,data, userlist, author) VALUES (?, ?, ?, ?)"
    userlist = [username]
    pickleduserlist = pickle.dumps(userlist)

    cursor.execute(query,(gridname,pickledgrid, pickleduserlist, username))
    con.commit()
    return


def createtableuser(con):
    
    cursor = con.cursor()
    query = "DROP TABLE IF EXISTS user"
    cursor.execute(query)
    con.commit()

    query = "CREATE TABLE user(username VARCHAR PRIMARY KEY, password VARCHAR, gridname VARCHAR, FOREIGN KEY(gridname) REFERENCES grid (gridname))"
    cursor.execute(query)
    con.commit()

def createtablegrid(con):
    
    cursor = con.cursor()
    query = "DROP TABLE IF EXISTS grid"
    cursor.execute(query)
    con.commit()

    query = "CREATE TABLE grid(gridname VARCHAR PRIMARY KEY, data VARCHAR, userlist VARCHAR, author VARCHAR)"
    cursor.execute(query)
    con.commit()


def server(ip, port):
    s = socket(AF_INET, SOCK_STREAM)

    
    con = sqlite3.connect('trainsim.db')
    cursor = con.cursor()
    
    # Create empty tables
    createtableuser(con)
    createtablegrid(con)
    # Create two default users
    query = "INSERT INTO user (username,password,gridname) VALUES (?, ?, ?)"
    cursor.execute(query,("doruk","123",None))
    query = "INSERT INTO user (username,password,gridname) VALUES (?, ?, ?)"
    cursor.execute(query,("hatice","456",None))
    con.commit()

    s.bind((ip,port))
    s.listen(10)    # 1 is queue size for "not yet accept()'ed connections"

    sim = Thread(target = simulator, args=())
    sim.start()

    try:
        while True:
        #for i in range(5):    # just limit # of accepts for Thread to exit
            ns, peer = s.accept()
            print(peer, "connected")
                # create a thread with new socket
            t = Thread(target = worker, args=(ns,))
            t.start()
            # now main thread ready to accept next connection
    finally:
        s.close()


if __name__ == '__main__':
	server('127.0.0.1', 34377)





