# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.models import User
from events.models import *
from athletes.models import Athlete
from client.models import *
from django.core.mail import EmailMessage
from multiprocessing import Pool, Queue
from events.views import *
import urllib2
from events.views import make_dir
import zipfile
from os import listdir
from pprint import pprint
from os.path import isfile, join
import PIL
from PIL import Image

event_bucket = 'ais-django'
from events.views import s3
import shutil
from events.views import rekog


def resize_image(p):
    mywidth = 800
    origWidth = 4500
    img = Image.open(p)
    wpercent = (mywidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    wpercent1 = (origWidth / float(img.size[0]))
    hsize1 = int((float(img.size[1]) * float(wpercent1)))
    # print('Processing %s/%s image---------------' % (count, files.__len__()))
    img = img.resize((mywidth, hsize), PIL.Image.ANTIALIAS)
    img1 = img.resize((origWidth, hsize1), PIL.Image.ANTIALIAS)
    img1.save(p)


def downloadFile(dbx_folder, url, event):
    local_dir = "AIS_PROJ/media/Events_Data"
    make_dir(local_dir)
    response = urllib2.urlopen(url)
    data = response.read()
    filename = "%s/%s.zip" % (local_dir, dbx_folder)
    file_ = open(filename, 'w+')
    file_.write(data)
    file_.close()
    extrct_path = "%s/%s" % (local_dir, dbx_folder)
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(extrct_path)
    print ("Extract Done")
    onlyfiles = [f for f in listdir(extrct_path) if isfile(join(extrct_path, f))]
    for img in onlyfiles:
        file_path = '%s/%s' % (extrct_path, img)
        if not file_path.endswith('.DS_Store'):
            name = os.path.splitext(img)[0]
            key = "Events/%s/%s.jpg" % (event.name, name)
            file = open(file_path, 'rb')
            object = s3.Object(event_bucket, key)
            object.put(Body=file, ContentType='image/jpeg', ACL='public-read')
            s3Url = "https://s3.amazonaws.com/%s/%s" % (event_bucket, key)
            dbx_path = '%s/%s' % (dbx_folder, img)
            event_image = EventImage()
            event_image.link = s3Url
            event_image.dbx_path = dbx_path
            event_image.save()
            event.image_links.add(event_image)
            event.save()
    if os.path.exists(filename):
        os.remove(filename)
    try:
        shutil.rmtree(extrct_path, ignore_errors=True)
    except:
        pass
    event.status = 's3processed'
    event.save()
    queue = ScanQueue.objects.filter(event=event, is_scanned=False)
    try:
        for q in queue:
            print ('starting for %s' % q.athlete.name)
            process = Process(target=image_process, args=(q.athlete, q.event,))
            process.start()
            q.is_scanned = True
            q.save()
    except:
        pass


def index(request):
    title = "Home"
    return render(request, 'client/index.html', {'title': title})


@csrf_exempt
def create_project(request):
    title = "Add project"
    host = request.get_host()
    msg = ''
    if request.method == 'POST':
        project_name = request.POST.get('projectName', '')
        email = request.POST.get('form-email', '')
        try:
            user = User.objects.get(username=email)
        except User.DoesNotExist:
            user = User()
            password = User.objects.make_random_password()
            user.set_password(password)
            user.username = email
            user.email = email
            user.save()
            athlete = Athlete()
            athlete.user = user
            athlete.name = email
            athlete.is_provider = True
            athlete.profile_complete = False
            athlete.save()
            msg = "Kindly check your email for account details"
            body = 'Welcome to FaceSpace.AI, Your account is been created\nusername: %s\npassword: %s' % (
                user.email, password)
            email = EmailMessage('FaceSpace.AI Account Setup', body, from_email=settings.from_email,
                                 to=[user.email])
            email.send()
        event = Event()
        dbx_folder = ""
        dbx_link = request.POST.getlist('dbx_link', '')
        dbx_name = request.POST.getlist('dbx_name', '')
        threshold = request.POST.get('threshold', '')
        event.name = project_name
        # event.dbx_link = dbx_link
        event.dropbox_Folder = dbx_folder
        event.threshold = int(threshold)
        event.user = user
        event.save()
        i = 0
        for link in dbx_link:
            event_image = EventImage()
            event_image.link = link
            event_image.dbx_path = '%s/%s' % (dbx_folder, dbx_name[i])
            event_image.name = dbx_name[i]
            i = i + 1
            event_image.save()
            event.image_links.add(event_image)
        event.save()
        url = "/projects/%s/join" % event.id
        # p = Process(target=downloadFile, args=(dbx_folder, dbx_link, event,))
        # p.start()
        event.status = 's3processed'
        event.save()
        queue = ScanQueue.objects.filter(event=event, is_scanned=False)
        try:
            for q in queue:
                print ('starting for %s' % q.athlete.name)
                process = Process(target=image_process, args=(q.athlete, q.event,))
                process.start()
                q.is_scanned = True
                q.save()
        except:
            pass
        try:
            body = 'Your Project %s has been created successfully' % event.name
            email = EmailMessage('FaceSpace.AI Project Creation', body, from_email=settings.from_email,
                                 to=[user.email])
            email.send()
        except:
            pass
        return JsonResponse({'url': url, 'msg': msg})
    return render(request, 'client/add_project.html', {'title': title, 'host': host})


@login_required
def projects(request, pk):
    title = "Projects"
    event = Event.objects.get(pk=pk)
    s3Images = event.s3images_set.all()
    return render(request, 'client/Projects.html', {'title': title, 'data_type': 'event', 'images': s3Images})


@login_required
def client_projects(request):
    title = "Projects"
    user = request.user
    projs = Event.objects.filter(user=user)
    return render(request, 'client/projects-table.html', {'title': title, 'projects': projs})


def image_process(athlete, project):
    try:
        task = Task.objects.get(athlete=athlete, event=project)
    except Task.DoesNotExist:
        task = Task.objects.create(athlete=athlete, event=project)
    task.status = 0
    task.save()
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
            print( filename )
            response = requests.get(image.link, stream=True)
            with open(filename, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            print(filename)
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
    try:
        task = Task.objects.get(athlete=athlete, event=project)
    except Task.DoesNotExist:
        task = Task.objects.create(athlete=athlete, event=project)
    task.status = 1
    task.save()
    body = "Project %s is completely scanned for %s" % (project.name, athlete.name)
    email = EmailMessage("FACE Space Scanning Report", body, from_email=settings.from_email,
                         to=[athlete.user.email, project.user.email])
    email.send()


def send_email(subject, body, from_email, to):
    email = EmailMessage(subject=subject, body=body, from_email=from_email, to=to)
    email.send()


@login_required
def join_project(request, pk):
    user = request.user
    next_url = '/projects/%s/join' % pk
    try:
        try:
            athlete = Athlete.objects.get(user=user)
        except Athlete.DoesNotExist:
            athlete = Athlete.objects.create(profile_complete=False)
            url = '/users/%s/update/?next=%s' % (athlete.pk, next_url)
            return redirect(url)
        if not athlete.profile_complete:
            url = '/users/%s/update/?next=%s' % (athlete.pk, next_url)
            return redirect(url)

        project = Event.objects.get(pk=pk)

        project.athletes.add(athlete)
        to = [athlete.user.email, project.user.email]
        body = "%s Joined project %s" % (athlete.name, project.name)
        try:
            p = Process(target=send_email, args=('Project Join Report', body, settings.from_email, to,))
            p.start()
        except:
            pass
        if project.status == 'NotProcessed':
            queue = ScanQueue()
            queue.event = project
            queue.athlete = athlete
            queue.save()
        else:
            try:
                print ('Process starting')
                process = Process(target=image_process, args=(athlete, project,))
                process.start()
            except Athlete.DoesNotExist:
                return redirect('all')
        task = Task.objects.create(event=project, athlete=athlete)

        return redirect('participated')
    except Event.DoesNotExist:
        pass


def privacy(request):
    return render(request, 'client/privacy-policy.html')


def terms(request):
    return render(request, 'client/terms-conditions.html')


@login_required
def sync_again(request, pk):
    event = Event.objects.get(pk=pk)
    athlete = Athlete.objects.get(user=request.user)
    process = Process(target=image_process, args=(athlete, event,))
    process.start()
    task = Task.objects.get(event=event, athlete=athlete)
    task.status = 0
    task.save()
    print (event, athlete, task)
    return JsonResponse({'success': True}, safe=False)