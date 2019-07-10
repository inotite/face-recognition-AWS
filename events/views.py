import urllib2
import requests
from django.core.mail import EmailMessage
from django.http import HttpResponse
# import face_recognition
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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
from AIS_PROJ import settings


def get_dbx():
    dbx = dropbox.Dropbox(settings.DROPBOX_OAUTH2_TOKEN)
    return dbx


def get_dpx_folders():
    dbx = dropbox.Dropbox(settings.DROPBOX_OAUTH2_TOKEN)
    arr = []
    for entry in dbx.files_list_folder(settings.DROPBOX_PATH).entries:
        arr.append(entry.name)
    return arr


s3 = boto3.resource('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
s3Client = boto3.client('s3', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
BUCKET = "ais-django"
rekognition = boto3.client('rekognition', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                           aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name='us-east-1')
dynamodb = boto3.client('dynamodb', aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY, region_name='us-east-1')


def make_dir(dir):
    if not os.path.exists(os.path.dirname(dir)):
        os.makedirs(os.path.dirname(dir))


@login_required
def index(request):
    title = "Events"
    domain = request.get_host()
    if request.user.is_superuser:
        events = Event.objects.all()
    else:
        events = Event.objects.filter(user=request.user)
    return render(request, "events/index.html",
                  {"title": title, 'events': events, 'domain': domain})


@login_required
def create(request):
    title = "Create Event"
    if request.method == 'POST':
        form = EventCreationForm(request.POST)
        if form.is_valid():
            event = form.save()
            # ret_url = "/events/"+event.pk+"/dropbox_to_s3"
            ret_url = "/%s/%d/%s" % ('events', event.pk, 'dropbox_to_s3')
            return redirect(ret_url)
    else:
        form = EventCreationForm()
    return render(request, 'athletes/create.html', {'title': title, 'form': form})


@login_required
def attach_dropbox(request, pk):
    event = Event.objects.get(pk=pk)
    arr = get_dpx_folders()
    if request.method == 'POST':
        event.dropbox_Folder = request.POST['arr']
        event.save()
        return redirect('/events')
    else:
        form = EventCreationForm(instance=event)
    return render(request, 'events/create.html', {'title': "attach dropboox", 'arr': arr})


@login_required
def delete(request, pk):
    event = Event.objects.get(pk=pk)
    title = "Delete " + event.name
    if request.method == 'POST':
        event.delete()
        return redirect('/events')
    else:
        return render(request, 'delete_form.html', {'title': title, 'object': event.name})


@login_required
def dropbox_to_s3(request, pk):
    dbx = get_dbx()
    start_time = time.time()
    title = 'Dropbox Scan'
    event = Event.objects.get(pk=pk)
    athletes = event.athletes.all()
    warning = ''
    if event.status == 'scanned':
        warning = "WARNING! This event is already completely processed. If you proceed to Sync again all the previous " \
                  "data will be lost "
    path = '%s%s' % (settings.DROPBOX_PATH, event.dropbox_Folder)

    files = dbx.files_list_folder(path).entries
    if request.method == 'POST':
        thresholdString = request.POST.get("sliderval")
        threshold = int(thresholdString)
        event.status = 'Processing'
        event.save()
        thumbLocal = '/media%s/' % path
        LocalFileDir = 'AIS_PROJ/media%s/' % path
        make_dir('AIS_PROJ/media%s/' % path)
        thumbs = '%sthumbs/' % LocalFileDir
        make_dir('AIS_PROJ%sthumbs/' % LocalFileDir)
        count = 0
        for file in files:
            count = count + 1
            dropbox_path = '%s/%s' % (path, file.name)
            print ('Downloading...%s' % dropbox_path)
            metadata, file_from_dbx = dbx.files_download(path=dropbox_path)
            p = "%s%s" % (LocalFileDir, file.name)
            make_dir(p)
            with open(p, 'w') as f:
                f.write(file_from_dbx.content)
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
            thumb = '%s%s' % (thumbs, file.name)
            make_dir(thumb)
            tl = '%sthumbs/%s' % (thumbLocal, file.name)
            img.save(thumb)
            # scan(athletes, event, thumb, dropbox_path, tl)

            # rekog(event, p, dropbox_path, tl, threshold)
            print ('Image processed. now deleting the original image..%s' % p)
            # if os.path.exists(p):
            #     os.remove(p)
        event.status = 'scanned'
        event.save()
        end_time = time.time()
        scanlog = ScanLog()
        scanlog.event = event
        scanlog.athletes = athletes.__len__()
        scanlog.dropbox_images = files.__len__()
        scanlog.time_taken = end_time - start_time
        scanlog.save()
    return render(request, 'events/dropbox_to_s3.html', {'event': event, 'files': files.__len__(),
                                                         'title': title, 'warning': warning})


def rekog(event, image_url, drop_path, tl, threshold, athlete):
    event_image = create_image(tl, drop_path, event)
    image = Image.open(image_url)
    stream = io.BytesIO()
    image.save(stream, format="JPEG")
    is_found = False
    image_binary = stream.getvalue()
    response = rekognition.detect_faces(
        Image={'Bytes': image_binary}
    )
    # response = rekognition.detect_faces(
    #     Image={
    #         'S3Object':{
    #             'Bucket':'ais-django',
    #             'Name':'Events/7_Juniors.jpg'
    #             }
    #         },
    #     Attributes=['ALL'])
    all_faces = response['FaceDetails']
    lengths = len(response['FaceDetails'])
    print( "Faces: %s" % lengths)
    # Initialize list object
    boxes = []
    # Get image diameters
    image_width = image.size[0]
    image_height = image.size[1]

    # Crop face from image
    face_idx = 0
    for face in all_faces:
        box = face['BoundingBox']
        x1 = int(box['Left'] * image_width) * 0.9
        y1 = int(box['Top'] * image_height) * 0.9
        x2 = int(box['Left'] * image_width + box['Width'] * image_width) * 1.10
        y2 = int(box['Top'] * image_height + box['Height'] * image_height) * 1.10
        image_crop = image.crop((x1, y1, x2, y2))

        print("Left: %s, Top: %s, Width: %s, Height %s" % (box['Left'] * image_width, box['Top'] * image_height, box['Width'] * image_width, box['Height']*image_height))

        face_idx = face_idx + 1

        with open("%sa%s.jpg" % (settings.MEDIA_ROOT, face_idx), 'wb') as out_file:
            image_crop.save(out_file, format="JPEG")
        stream = io.BytesIO()
        # print(image_crop)
        image_crop.save(stream, format="JPEG")
        image_crop_binary = stream.getvalue()
        try:
            #  print ('threshold: ')
            # print (threshold)
            # Submit individually cropped image to Amazon Rekognition
            print("AWS Rekognition")
            response = rekognition.search_faces_by_image(
                CollectionId='BLUEPRINT_COLLECTION',
                Image={'Bytes': image_crop_binary},
                FaceMatchThreshold=int(threshold),
            )
            if len(response['FaceMatches']) > 0:
                # Return results
                #  print ('Coordinates ', box)
                for match in response['FaceMatches']:
                    print ('Similarity: ' + "{:.2f}".format(match['Similarity']) + "%")
                    # image_crop.save(open("%sa%s.jpg" % (settings.MEDIA_ROOT, match['Face']['FaceId']), 'wb'), format="JPEG")
                    face = dynamodb.get_item(
                        TableName='athletes_data',
                        Key={'RekognitionId': {'S': match['Face']['FaceId']}}
                    )
                    if 'Item' in face:
                        person = face['Item']['FullName']['S']
                        athlete_id = int(face['Item']['athlete_id']['S'])
                        print(athlete_id)
                        print(athlete.id)
                        if athlete_id == athlete.id:
                            try:
                                event_image.athlete.add(Athlete.objects.get(pk=athlete_id))
                                is_found = True
                                print( "Found---------------------------")
                                image_crop.save(open("%sFound%s.jpg" % (settings.MEDIA_ROOT, match['Face']['FaceId']), 'wb'), format="JPEG")
                            except:
                                pass
                            event_image.save()
                        else:
                            print ('current user not in this image')
                    else:
                        person = 'no match found'
                        athlete_id = -1

                #  print (match['Face']['FaceId'], match['Face']['Confidence'], person,athlete_id)
            else:
                print ('unknown found')

        except Exception as e:

            print (e)
    pic_log = PicLog.objects.create(pic_link=tl, event=event, athlete=athlete, is_person_found=is_found)
    if is_found:
        pic_log.comment = "This person was FOUND in this image at Threshold: %s\nTo verify visit the link above" % str(
            threshold)
        print(pic_log.comment)
    else:
        pic_log.comment = "This person was NOT FOUND in this image at Threshold: %s\nTo verify visit the link above" % str(
            threshold)
    pic_log.save()


def create_image(local_url, dbx_url, event):
    try:
        # print("trying to get s3 images")
        print("Local Url: %s, Dropbox Url: %s, " % (local_url, dbx_url))
        image = s3Images.objects.get(s3Url=local_url, event=event)
    except s3Images.DoesNotExist:
        print("Image doesn't exist")
        image = s3Images()

    # print("Image")

    image.event = event
    image.dropbox_Url = dbx_url
    image.s3Url = local_url
    image.save()
    print(image)
    return image


def saveImage(event, athlete_id, tl, drop_path):
    final_image = s3Images()
    final_image.event = event
    final_image.athlete = Athlete.objects.get(pk=athlete_id)
    final_image.s3Url = tl
    final_image.dropbox_Url = drop_path
    final_image.save()


def absoluteFilePaths(directory):
    eventImages = []
    for dirpath, _, filenames in os.walk(directory):
        for f in filenames:
            eventImages.append(os.path.abspath(os.path.join(dirpath, f)))
    return eventImages


def to_jpg(imageUrl):
    if not imageUrl.endswith('jpg'):
        new = os.path.splitext(imageUrl)[0] + '.jpg'
        Image.open(imageUrl).convert('RGB').save(new)
        return new
    else:
        return imageUrl


@login_required
def getcsv(request):
    if request.method == 'POST':
        pk = int(request.POST['event_id'])
        folder = request.POST['dbx_path']
        event = Event.objects.get(pk=pk)
        im = event.s3images_set.all()
        images = im
        name = 'AIS_PROJ/media/%s.csv' % (event.name)
        response = HttpResponse(content_type='text/csv')
        resp = '%s_%s.csv' % (event.name, datetime.now())
        response['Content-Disposition'] = 'attachment; filename="' + resp
        writer = csv.writer(response)
        writer.writerow(['ID', 'Name', 'Headshot', 'Event'])

        for item in images:
            if item.athlete:
                for ath in item.athlete.all():
                    # Write item to outcsv
                    writer.writerow([ath.id, ath.name, '%s%s' % (folder, item.dropbox_Url), event.name])
        return response
    return redirect('index')


def get_event_csv(request, pk):
    now = datetime.now()
    event = Event.objects.get(pk=pk)
    print (now)
    person_resource = EventResource(isinstance(event))
    dataset = person_resource.export()
    response = HttpResponse(dataset.csv, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Event_%s.csv"' % now
    return response


@login_required
def event_gallary(request, pk):
    event = Event.objects.get(pk=pk)
    s3Images = event.s3images_set.all()
    title = '%s Gallery' % event.name
    url = '#'
    links = event.image_links.all()
    if request.method == 'POST':
        athleteID = request.POST['athlete']
        eventID = request.POST['event']
        fileKey = 'AthletesResults/A%s_E%s.zip' % (athleteID, eventID)
        url = s3Client.generate_presigned_url('get_object',
                                              Params={
                                                  'Bucket': BUCKET,
                                                  'Key': fileKey,
                                              },
                                              ExpiresIn=3600,
                                              HttpMethod='get')
        print (url)
    return render(request, 'gallary.html',
                  {'image_links': links, 'title': title, 'data': event, 'data_type': 'event', 'images': s3Images,
                   'url': url,
                   'imagecount': s3Images.__len__()})


@login_required
def gallary(request, pk):
    event = Event.objects.get(pk=pk)
    s3Images = event.s3images_set.all()
    title = '%s Gallery' % event.name
    url = '#'
    return render(request, 'tagged_gallary.html',
                  {'title': title, 'data': event, 'data_type': 'event', 'images': s3Images, 'url': url,
                   'imagecount': s3Images.__len__()})


@login_required
def Tags(request, pk):
    # print "in tags"
    event = Event.objects.get(pk=pk)
    athletes = event.athletes.all()
    Tags = event.s3images_set.all()
    if request.method == 'POST':
        ids = request.POST.getlist('athlete')
        imageid = request.POST['ImageId']
        image = s3Images.objects.get(pk=imageid)
        for ath in image.athlete.all():
            image.athlete.remove(ath)
        image.save()
        for aID in ids:
            athlete = athletes.get(pk=aID)
            try:
                image.athlete.add(athlete)
            except Exception as e:
                print (e)
        image.save()
    return render(request, 'events/unknown.html',
                  {'Tags': Tags, 'title': 'Tag Images', 'event': event, 'athletes': athletes})


@login_required
def delete_unmach(request, pk, event):
    obj = s3Images.objects.get(pk=pk)
    obj.delete()
    ret = "/events/%s/Tags" % event
    print (ret)
    return redirect(ret)


@login_required
def stats(request, pk):
    event = Event.objects.get(pk=pk)
    title = "%s images" % event.name
    atheletes = event.athletes.all()
    data = []
    for athelete in atheletes:
        images = athelete.s3images_set.all()
        images = images.filter(event_id=pk)
        d = {'xData': athelete.name, 'yData': images.__len__()}
        data.append(d)
    json_data = json.dumps(data)
    return render(request, 'graph.html', {'json_data': json_data, 'title': title})


class ImagesViewset(viewsets.ModelViewSet):
    def get_queryset(self):
        pk = self.kwargs['pk']
        return s3Images.objects.filter(event_id=pk)

    queryset = s3Images.objects.all()
    serializer_class = s3ImagesSerialize


def dataTable(request, pk):
    event = Event.objects.get(pk=pk)
    athletes = event.athletes.all()
    Tags = event.s3images_set.all()
    if request.method == 'POST':
        ids = request.POST.getlist('athlete')
        imageid = request.POST['ImageId']
        image = s3Images.objects.get(pk=imageid)
        for aID in ids:
            athlete = athletes.get(pk=aID)
            try:
                image.athlete.add(athlete)
            except Exception as e:
                print (e)
        image.save()
        print (ids)
    return render(request, 'events/datatable.html',
                  {'event': event, 'Tags': Tags, 'title': 'Tag Images', 'athletes': athletes})


from django.core import serializers
from django.http import HttpResponse


def getAthletes(request, pk):
    event = Event.objects.get(pk=pk)
    athletes = event.athletes.all()

    qs_json = serializers.serialize('json', athletes)
    print (qs_json)
    return HttpResponse(qs_json, content_type='application/json')


def reprocess_all(event):
    athletes = event.athletes.all()
    for athlete in athletes:
        athlete.s3images_set.all().delete()
        print ('reprocessing %s, %s' % (athlete.name, athlete.id))
        # print("-------------------start list------------------")
        # print ("Faces in collection: BLUEPRINT_COLLECTION")

        # collectionId = "BLUEPRINT_COLLECTION"
        # tokens = True
        # response=rekognition.list_faces(CollectionId=collectionId,
        #                        MaxResults=2)

        # while tokens:

        #     faces=response['Faces']

        #     for face in faces:
        #         print (face)
        #     print("------External Image Id")
            
        #     print("**************************")

        #     print("-------------------------")
        #     if 'NextToken' in response:
        #         nextToken=response['NextToken']
        #         response=rekognition.list_faces(CollectionId=collectionId,
        #                                 NextToken=nextToken,MaxResults=2)
        #     else:
        #         tokens=False
        
        # print("-------------------end list------------------")
        image_process(athlete=athlete, project=event)
        try:
            task = Task.objects.get(event=event, athlete=athlete)
            print ('TASK GET')

        except Task.DoesNotExist:
            task = Task.objects.create(event=event, athlete=athlete)
            print ('TASK CREATED')

        task.status = 0
        task.save()


def rescan(request, pk):
    event = Event.objects.get(pk=pk)
    if request.method == 'POST':
        threshold = int(request.POST['threshold'])
        event.threshold = threshold
        event.save()
        process = Process(target=reprocess_all, args=(event,))
        process.start()
        return redirect('/events')
    return render(request, 'events/dropbox_to_s3.html', {'event': event})


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
            # print (image.link)
            filename = ""

            local_dir = "%sEvents_Data" % settings.MEDIA_ROOT
            # make_dir(local_dir)

            filename = "%s/%s.jpg" % (local_dir, image.id)
            make_dir(filename)
            response = requests.get(image.link, stream=True)
            # print(filename)
            print("Response %s" % response.raw)
            with open(filename, 'wb') as out_file:
                # print( "File Opened")
                shutil.copyfileobj(response.raw, out_file)
            # del response
            # print ("Resize Image")
            # try:
            #     resize_image(filename)
            # except:
            #     pass
            print("Rekog started")
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
    task.status = 1
    task.save()

    try:
        body = "Project %s is completely scanned for %s" % (project.name, athlete.name)
        email = EmailMessage("FACE Space Scanning Report", body, from_email=settings.from_email,
                             to=[athlete.user.email, project.user.email])
        email.send()
        print (body)
    except:
        pass


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