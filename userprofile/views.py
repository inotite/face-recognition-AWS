# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import base64
import os

from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages

from athletes.models import Athlete
from .forms import UserCreationForm1
from django.contrib.auth import update_session_auth_hash
import face_recognition
from AIS_PROJ import settings
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in

bucket = 'novatore-ais'
from events.views import s3, s3Client
import PIL
from PIL import Image


# def resize_image(p):
#     mywidth = 800
#     origWidth = 500
#     img = Image.open(p)
#     wpercent = (mywidth / float(img.size[0]))
#     hsize = int((float(img.size[1]) * float(wpercent)))
#     wpercent1 = (origWidth / float(img.size[0]))
#     hsize1 = int((float(img.size[1]) * float(wpercent1)))
#     # print('Processing %s/%s image---------------' % (count, files.__len__()))
#     img = img.resize((mywidth, hsize), PIL.Image.ANTIALIAS)
#     img1 = img.resize((origWidth, hsize1), PIL.Image.ANTIALIAS)
#     img1.save(p)

def index(request):
    return redirect('client-index')


def signup(request):
    title = "Signup"
    next_url = request.GET.get('next', '')
    imageErr = ''
    if request.method == 'POST':
        form = UserCreationForm1(request.POST)
        if form.is_valid():
            file = request.FILES.get('image')
            uploaded_file = request.FILES['image']
            image = face_recognition.load_image_file(file)
            enc = face_recognition.face_encodings(image)
            noOfFaces = enc.__len__()
            if noOfFaces == 1:
                # try:
                form.save()
                user = form.save()
                username = form.cleaned_data.get('username')
                user.username = username.lower()
                user.email = username.lower()
                user.save()
                athlete = Athlete()
                athlete.user = user
                athlete.name = user.first_name
                athlete.image = file
                athlete.save()
                id = str(athlete.id)  # type: str
                key = "%s_%s.jpg" % (user.first_name, athlete.id)
                url = "AIS_PROJ/%s" % athlete.image.url
                # resize_image(url)
                file = open(url, 'rb')
                object = s3.Object(bucket, key)
                object.put(Body=file, ContentType='image/jpeg', ACL='public-read',
                           Metadata={'fullname': athlete.name, 'athlete_id': id})
                s3Url = "https://s3.amazonaws.com/%s/%s" % (bucket, key)
                athlete.s3ImageUrl = s3Url
                athlete.save()
                path_to_file = '%s/%s' % (settings.BASE_DIR, url)
                print (path_to_file)
                # if os.path.exists(path_to_file):
                #     os.remove(path_to_file)
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                if next_url or next_url.__len__() > 0:
                    return redirect(next_url)
                return redirect('/events')
                # except:
                #     imageErr="Error in creating your account. try again later"
            else:
                imageErr = 'The Image has %s faces in it\n Please upload image with only one face in it.' % noOfFaces

    else:
        form = UserCreationForm1()
    return render(request, 'userprofile/signup.html', {'form': form, 'title': title, 'imageErr': imageErr})


@login_required
def change_password(request):
    title = "Change Password"
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('/events')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'userprofile/change_password.html', {
        'form': form,
        'title': title
    })


@receiver(user_logged_in)
def set_image_session(sender, user, request, **kwargs):
    try:
        athlete = Athlete.objects.get(user=user)
    except Athlete.DoesNotExist:
        return
    request.session['image'] = athlete.s3ImageUrl
    return


def forgot_password(request):
    msg = ""
    if request.method == "POST":
        email = request.POST.get('email', '')
        user = User.objects.get(username=email)
        password = User.objects.make_random_password()
        user.set_password(password)
        user.username = email
        user.email = email
        user.save()
        msg = "Kindly check your email for Password"
        body = 'Your account is been Restored\nusername: %s\npassword: %s' % (
            user.email, password)
        email = EmailMessage('FaceSpace.AI Password Reset', body, from_email=settings.from_email,
                             to=[user.email])
        email.send()

    return render(request, 'userprofile/reset-password.html', {'msg': msg})


def login_auth(request):
    msg = ''
    form = AuthenticationForm()
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username.lower(), password=password)
        if user is not None:

            try:
                athlete = Athlete.objects.get(user=user)
            except Athlete.DoesNotExist:
                return
            request.session['image'] = athlete.s3ImageUrl
            login(request, user)
            try:
                next = request.GET.get('next', '')
                return redirect(next)
            except:
                return redirect('/events')
        else:
            msg = "Invalid login details"

    return render(request, 'userprofile/login.html', {'msg': msg, 'form': form})
