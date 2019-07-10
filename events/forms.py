from django import forms
from django.urls import reverse
from .models import Event
from django.utils.safestring import mark_safe
import dropbox
from AIS_PROJ import settings


def get_dpx_folders():
    #dbx=dropbox.Dropbox(settings.DROPBOX_OAUTH2_TOKEN)
    arr=[('','--select--')]
    # for entry in dbx.files_list_folder(settings.DROPBOX_PATH).entries:
    #     arr.append((entry.name,entry.name))
    return arr


class EventCreationForm(forms.ModelForm):
    arr=get_dpx_folders()
    dropbox_Folder=forms.ChoiceField(choices=arr, required=True, label='Dropbox Folder')

    class Meta:
        model = Event
        fields = ('dropbox_Folder',)
