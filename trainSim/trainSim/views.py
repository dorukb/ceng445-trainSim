from ast import operator
from pickletools import read_bytes1
from unicodedata import name
from urllib import request
from django.shortcuts import render,redirect
from django.http import HttpResponse
from trainSim.models import *
from trainSim.forms import *

from django.contrib.auth.decorators import login_required
from trainSim import trainLib as lib
import pickle
from django.db import models

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

@login_required
def index(request, message = ''):
    Grids = Grid.objects.all()

    gridstodisplay = []
    for grid in Grids:
        accesslist = pickle.loads(grid.UserIDList)
        if(request.user.username in accesslist):
            gridstodisplay.append(grid)

    return render(request, 'MyGrids.html', {'Grids': gridstodisplay})

@login_required
def createGrid(request,uid=None):
    if request.user:
        gridform = gridForm()
        operation = 'insert'
    
    return render(request, 'gridform.html',{'uid': uid, 'form': gridform, 'operation': operation})
            
@login_required
def create(request):
    p = request.POST

    row = int(p['row'])
    col = int(p['column'])
    name = p['name']

    print("create grid", row, col ,name)
    grid = lib.GameGrid(row,col)
    userList = [request.user.username]
    auth = request.user
    data = pickle.dumps(grid)
    users = pickle.dumps(userList)
    print("dumped data: ", data)
    print("dumped users:", users)

    g = pickle.loads(data)
    print("loaded g:", g)

    newgrid = Grid.objects.create(gridname = name,
			data  =pickle.dumps(grid),
			UserIDList = pickle.dumps(userList),
			author = auth)
	
    return redirect("/") 


@login_required
def share(request, gridname):
    print("SHARE called")

    p = request.POST
    grid = Grid.objects.get(gridname = gridname)
    accessList = pickle.loads(grid.UserIDList)

    username = request.user.username
    if username == grid.author:
        print("has sharing rights.")
        users = User.objects.all()
        for user in users:
            if(user.username not in accessList):
                accessList.append(user.username)
                print("added user: ", user.username, " to accesslist of: ", gridname)
        
        pickledlist = pickle.dumps(accessList)
        updatedgrid = Grid.objects.filter(gridname = gridname).update(UserIDList = pickledlist)

    else:
        print("You can not share this grid, you are not the author.")

    return redirect('/')

@login_required
def hatice(request, gridname):
    print("hatice called")
    grid = Grid.objects.get(gridname = gridname)
    accessList = pickle.loads(grid.UserIDList)

    username = request.user.username
    if username == grid.author:
        print(username, " has shared the grid ", gridname)
        accessList = [grid.author]
        pickledlist = pickle.dumps(accessList)
        updatedgrid = Grid.objects.filter(gridname = gridname).update(UserIDList = pickledlist)
    else:
        print("You can not unshare this grid, you are not the author.")
   
    return redirect('/')

@login_required
def attach(request, gridname):
    p = request.POST

    grid = Grid.objects.get(gridname = gridname)
    print("grid: ", grid)

    users = pickle.loads(grid.UserIDList)
    username = request.user.username
    print("req user:", request.user.username)
    print("users list:",users)

    if username in users:
        #update user as a list!!!!
        try:
            a = AttachedGrid.objects.get(user = request.user)
            print("already attached")
        except:
            print("attaching to grid")
            AttachedGrid.objects.create(attachedgrid = grid, user = request.user)

        griddata = pickle.loads(grid.data)
        addform = addForm()
        return render(request, 'edit.html',{'griddata': griddata,'addform': addform, 'gridname': gridname})
        #then pickle, update
    else:
        return redirect('/')
    # griddata = pickle.loads(grid.data)
    # addform = addForm()
    # return render(request, 'edit.html',{'griddata': griddata,'addform': addform, 'gridname': gridname})

@login_required
def detach(request, gridname):
    p = request.POST

    grid = Grid.objects.get(gridname = gridname)
    users = pickle.loads(grid.UserIDList)
    username = request.user.username

    if username in users:
        try:
            a = AttachedGrid.objects.get(user = request.user)
            if(a.attachedgrid.gridname == gridname):
                AttachedGrid.objects.get(user = request.user).delete()
                print("User ", username, " detached from ", gridname)
            else:
                print("Attached to another grid.")
        except:
            print("Not attached to any grid")
    
    return redirect('/')

@login_required
def delete(request, gridname):
    p = request.POST
    print("delete request for grid: ", gridname)
    Grid.objects.filter(gridname=gridname).delete()

    return redirect('/')
    # Grids = Grid.objects.all()
    # return render(request, 'MyGrids.html', {'Grids': Grids})

@login_required
def edit(request, gridname):
    p = request.POST
    print("received name:", gridname)
    grid = Grid.objects.get(gridname = gridname)
    griddata = pickle.loads(grid.data)

    addform = addForm()
    return render(request, 'edit.html',{'griddata': griddata,'addform': addform, 'gridname': gridname})


@login_required
def gosim(request, gridname):
    p = request.POST
    grid = Grid.objects.get(gridname = gridname)
    griddata = pickle.loads(grid.data)
    trainPositions = griddata.getTrainPositions() # return list of list of tuples[(x,y), (x2,y2)]
       
    allDisplay = [] # list of strings
    for train in trainPositions:
        i = 0
        trainPosText ="" # each string shows engine and wagon positions for that train
        for wagonPos in train:
            if(i == 0):
                trainPosText +=  "Engine (" + str(wagonPos[0]) + "," + str(wagonPos[1]) + ") "
            else:
                trainPosText +=  "Wagon " + str(i) + " (" + str(wagonPos[0]) + "," + str(wagonPos[1]) + ") "
            i+=1
        allDisplay.append(trainPosText)                                

    return render(request, 'sim.html',{'griddata': griddata,'gridname': gridname, 'trainPosition': allDisplay})

@login_required
def commands(request):
    p = request.POST
    addform = addForm()

    if('addelm' in request.POST):
        row = p['row']
        col = p['col']
        tile = p['tile']
        if(not tile or not row or not col):
            print("Usage for add element: <row> <col> <tileType>")
            gridname = p['gridname']
            grid = Grid.objects.get(gridname = gridname)
            griddata = pickle.loads(grid.data)
            return render(request, 'edit.html',{'griddata': griddata,'addform': addform,'gridname': gridname})

        row = int(p['row'])
        col = int(p['col'])
        gridname = p['gridname']
        print(row, col, tile, " on grid: ", gridname)

        grid = Grid.objects.get(gridname = gridname)
        griddata = pickle.loads(grid.data)
        griddata.addElement(getnewelem(tile, griddata), row, col)
        
        pickledgrid = pickle.dumps(griddata)
        updatedgrid = Grid.objects.filter(gridname = p['gridname']).update(data = pickledgrid)
        return render(request, 'edit.html',{'griddata': griddata,'addform': addform,'gridname': gridname})

    elif('removeelm' in request.POST):
        print("remove element clicked")

        if(not p['row'] or not p['col']):
            print("Usage for remove element: <row> <col>")
            gridname = p['gridname']
            grid = Grid.objects.get(gridname = gridname)
            griddata = pickle.loads(grid.data)
            return render(request, 'edit.html',{'griddata': griddata,'addform': addform,'gridname': gridname})
        row = int(p['row'])
        col = int(p['col'])


        gridname = p['gridname']
        print("REMOVE COMMAND: ", row, col, " on grid: ", gridname)

        grid = Grid.objects.get(gridname = gridname)
        griddata = pickle.loads(grid.data)
        griddata.removeElement(row, col)
        
        pickledgrid = pickle.dumps(griddata)
        updatedgrid = Grid.objects.filter(gridname = p['gridname']).update(data = pickledgrid)
        return render(request, 'edit.html',{'griddata': griddata,'addform': addform,'gridname': gridname})

    elif('rotate' in request.POST):

        if(not p['rotationCount'] or not ['row'] or not p['col']):
            print("Usage for rotate element: <row> <col> <rotationCount>")
            gridname = p['gridname']
            grid = Grid.objects.get(gridname = gridname)
            griddata = pickle.loads(grid.data)
            return render(request, 'edit.html',{'griddata': griddata,'addform': addform,'gridname': gridname})

        row = int(p['row'])
        col = int(p['col'])
        rotCount =  int(p['rotationCount'])
        gridname = p['gridname']
        print("ROTATE COMMAND: ", row, col, " on grid: ", gridname)
        
        grid = Grid.objects.get(gridname = gridname)
        griddata = pickle.loads(grid.data)
        cell = griddata.getCell(row,col)
        cell.setOrientation(rotCount)

        pickledgrid = pickle.dumps(griddata)
        updatedgrid = Grid.objects.filter(gridname = p['gridname']).update(data = pickledgrid)
        return render(request, 'edit.html',{'griddata': griddata,'addform': addform,'gridname': gridname})

    elif('chstate' in request.POST):
        if(not ['row'] or not p['col']):
            print("Usage for ch state element: <row> <col>")
            gridname = p['gridname']
            grid = Grid.objects.get(gridname = gridname)
            griddata = pickle.loads(grid.data)
            return render(request, 'edit.html',{'griddata': griddata,'addform': addform,'gridname': gridname})

        row = int(p['row'])
        col = int(p['col'])
        gridname = p['gridname']
        print("CHSTATE COMMAND: ", row, col, " on grid: ", gridname)
        
        grid = Grid.objects.get(gridname = gridname)
        griddata = pickle.loads(grid.data)
        cell = griddata.getCell(row,col)
        cell.switchState()

        pickledgrid = pickle.dumps(griddata)
        updatedgrid = Grid.objects.filter(gridname = p['gridname']).update(data = pickledgrid)
        return render(request, 'edit.html',{'griddata': griddata,'addform': addform,'gridname': gridname})

    elif('step' in request.POST):
        gridname = p['gridname']
        grid = Grid.objects.get(gridname = gridname)
        griddata = pickle.loads(grid.data)
        griddata.advanceSim()

        trainPositions = griddata.getTrainPositions() # return list of list of tuples[(x,y), (x2,y2)]
        allDisplay = [] # list of strings
        for train in trainPositions:
            i = 0
            trainPosText ="" # each string shows engine and wagon positions for that train
            for wagonPos in train:
                if(i == 0):
                    trainPosText +=  "Engine (" + str(wagonPos[0]) + "," + str(wagonPos[1]) + ") "
                else:
                    trainPosText +=  "Wagon " + str(i) + " (" + str(wagonPos[0]) + "," + str(wagonPos[1]) + ") "
                i+=1
            allDisplay.append(trainPosText)         

        pickledgrid = pickle.dumps(griddata)
        updatedgrid = Grid.objects.filter(gridname = p['gridname']).update(data = pickledgrid)
        return render(request, 'sim.html',{'griddata': griddata,'gridname': gridname, 'trainPosition': allDisplay})

    else:
        print("unrecognized command")
