from pickle import TRUE
from tkinter import CASCADE
from django.db import models
from django.contrib.auth.models import User



class Grid(models.Model):
    gridname = models.CharField(max_length=20,primary_key= TRUE)
    data = models.CharField(max_length=2048)
    UserIDList = models.CharField(max_length=1024)
    author = models.CharField(max_length=20)
    def __str__(self):
	    return self.gridname

class AttachedGrid(models.Model):
    attachedgrid = models.ForeignKey(Grid, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
	    return self.attachedgrid