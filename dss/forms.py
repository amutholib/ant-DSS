from django import forms
from .models import SateliteAnomaly

"""
class DssForm(forms.Form):
    BUS_TYPE_CHOICES = [
        ('type1', 'Type 1'),
        ('type2', 'Type 2'),
        ('type3', 'Type 3'),
    ]
    ORBIT_TYPE_CHOICES = [
        ('LEO', 'Low Earth Orbit'),
        ('MEO', 'Medium Earth Orbit'),
        ('GEO', 'Geostationary Orbit'),
    ]
    MISSION_CHOICES = [
        ('typeA', 'Type A'),
        ('typeB', 'Type B'),
        ('typeC', 'Type C'),
    ]

    bustype         = forms.ChoiceField(choices=BUS_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), required=False)
    orbitcategory   = forms.ChoiceField(choices=ORBIT_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), required=False)
    missionprimary  = forms.ChoiceField(choices=MISSION_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}), required=False)
    
"""

class DssModelForm(forms.ModelForm):
    class Meta:
        model = SateliteAnomaly
        fields = ['bustype', 'orbitcategory', 'missionprimary']
        widgets = {
            'bustype': forms.Select(attrs={'class': 'form-select'}),
            'orbitcategory': forms.Select(attrs={'class': 'form-select'}),
            'missionprimary': forms.Select(attrs={'class': 'form-select'}),
        }