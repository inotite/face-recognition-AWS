import urllib2
import requests
from django.core.mail import EmailMessage
from django.http import HttpResponse
# import face_recognition
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from client.views import resize_image, rekog
from events.views import make_dir
from .models import *
from .forms import EventCreationForm
import dropbox
from AIS_PROJ import settings
import boto3
import os
from pathlib import Path
import shutil
import PIL
from PIL import Image
import json
import csv
import time
from .resources import EventResource
from datetime import datetime
import io
from django.db.models import Q
from rest_framework import viewsets, generics
from .serializers import s3ImagesSerialize
from multiprocessing import Process


def image_process(athlete, project):
    print ("scan Started")
    start_time = time.time()
    images = project.image_links.all()
    for image in images:
        # s3_image=
        try:
            print (image.link)
            filename = ""

            local_dir = "AIS_PROJ/media/Events_Data"
            make_dir(local_dir)

            filename = "%s/%s.jpg" % (local_dir, image.id)
            response = requests.get(image.link, stream=True)
            with open(filename, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            print (filename)
            try:
                resize_image(filename)
            except:
                pass
            rekog(project, filename, image.dbx_path, image.link, project.threshold, athlete)

            if os.path.exists(filename):
                os.remove(filename)
            print ("Image scanded")
        except:
            pass
    end_time = time.time()
    scanlog = ScanLog()
    scanlog.event = project
    scanlog.athletes = 1
    scanlog.athlete = athlete
    scanlog.dropbox_images = images.__len__()
    scanlog.time_taken = end_time - start_time
    scanlog.save()
    task = Task.objects.get(athlete=athlete, event=project)
    task.status = 1
    task.save()
    body = "Project %s is completely scanned for %s" % (project.name, athlete.name)
    email = EmailMessage("FACE Space Scanning Report", body, from_email=settings.from_email,
                         to=[athlete.user.email, project.user.email])
    email.send()
