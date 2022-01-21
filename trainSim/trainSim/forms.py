from django import forms

class gridForm(forms.Form):
	
	row = forms.IntegerField(label = "Row", min_value = 0, required = True)
	column = forms.IntegerField(label = "Column", min_value = 0, required = True)
	name = forms.CharField(label='Grid Name', max_length=20, required = True)

class addForm(forms.Form):
	row = forms.IntegerField(label = "Row", min_value = 0, required = False)
	col = forms.IntegerField(label = "Column", min_value = 0, required = False)
	tile = forms.CharField(label='Tile Type', max_length=40, required = False)
	rotationCount = forms.IntegerField(label = "Rotation Count", min_value = 0, required = False)

class removeForm(forms.Form):
	row = forms.IntegerField(label = "Row", min_value = 0, required = True)
	col = forms.IntegerField(label = "Column", min_value = 0, required = True)
