from ast import operator
from pickletools import read_bytes1
from unicodedata import name
from urllib import request
from django.shortcuts import render,redirect
from django.http import HttpResponse
from trainSim.models import *
from trainSim.forms import gridForm as gform
from django.contrib.auth.decorators import login_required
from trainSim import trainLib as lib
import pickle

@login_required
def index(request, message = ''):
    Grids = Grid.objects.all()

    #return HttpResponse(Grids)
    return render(request, 'MyGrids.html', {'Grids': Grids})

@login_required
def createGrid(request,uid=None):
    if request.user:
        gridform = gform()
        operation = 'insert'
    
    return render(request, 'gridform.html',{'uid': uid, 'form': gridform, 'operation': operation})
            
@login_required
def create(request):
    p = request.POST

    row = int(p['row'])
    col = int(p['column'])
    name = p['name']
    grid = lib.GameGrid(row,col)
    userList = [request.user]
    auth = request.user
    data = pickle.dumps(grid)
    users = pickle.dumps(userList)
    newgrid = Grid.objects.create(gridname = name,
			data  = data,
			UserIDList = users,
			author = auth)
	
    return redirect("/") 

@login_required
def edit(request,gridname):
    p = request.POST
    if 'attach' in request.POST:
        name  = gridname
        grid = Grid.objects.filter(gridname = name)
        users = pickle.loads(grid.UserIDList)
        if request.user in users:
            #update user as a list!!!!
            AttachedGrid.objects.create(attachedgrid = name, user = request.user)
            #then pickle, update
    
    return redirect("/") 
    



	