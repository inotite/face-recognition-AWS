from .models import Athlete
from django import forms


class AthleteCreationForm(forms.ModelForm):
    image = forms.ImageField(required=True,label='Headshot')

    class Meta:
        model = Athlete
        fields = ('name', 'image')
