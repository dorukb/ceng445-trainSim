from ast import operator
from django.shortcuts import render,redirect
from django.http import HttpResponse
from trainSim.models import *
from trainSim.forms import gridForm as gform
from django.contrib.auth.decorators import login_required

@login_required
def index(request, message = ''):
    Grids = Grid.objects.all()

	#return HttpResponse("Hello, this is trainSim")
    return render(request, 'MyGrids.html', {'message': message})

@login_required
def createGrid(request,uid):
    if request.user:
        gridform = gform()
        operation = 'insert'
            
