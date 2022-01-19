from django import forms

class Grid(forms.Form):
	
	row = forms.IntegerField(label = "Row", min_value = 0, required = True)
	column = forms.IntegerField(label = "Column", min_value = 0, required = True)
	name = forms.CharField(label='Grid Name', max_length=20, required = True)
