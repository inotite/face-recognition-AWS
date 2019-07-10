import face_recognition
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from AIS_PROJ import settings
from .forms import AthleteCreationForm
from .models import *
from events.models import *
from events.views import s3Client, BUCKET
from django.http import HttpResponse, JsonResponse
import json
from .resources import AthleteResource
from datetime import datetime
import csv
import os
import requests

bucket = 'novatore-ais'
from events.views import s3


@login_required
def export_data(request):
    response = ''
    now = datetime.now()
    print (now)
    if request.method == 'POST':
        person_resource = AthleteResource()
        event_pk = request.POST.get('event_pk', '')
        if event_pk.__len__() > 0:
            event = Event.objects.get(pk=event_pk)
            dataset = person_resource.export(event.athletes.all())
        else:
            dataset = person_resource.export()

        if request.POST['type'] == 'json':
            response = HttpResponse(dataset.json, content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="Athletes_%s.json"' % now
        if request.POST['type'] == 'csv':
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="Athletes_%s.csv"' % now
        if request.POST['type'] == 'xls':
            response = HttpResponse(dataset.xls, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = 'attachment; filename="Athletes_%s.xls"' % now
    return response


@login_required
def import_data(request):
    if request.method == 'POST':
        try:
            file = request.FILES.get('importFile')
            fstring = file.read()
            # create list of dictionaries keyed by header row
            csv_dicts = [{k: v for k, v in row.items()} for row in
                         csv.DictReader(fstring.splitlines(), skipinitialspace=True)]
            print (csv_dicts)
            print ('Adding athletes...')
            for row in csv_dicts:
                athlete = Athlete.objects.filter(pk=row['ID'])
                if not athlete:
                    print (row['ID'])
                    athlete = Athlete()
                    athlete.id = row['ID']
                    athlete.name = row['Name']
                    athlete.s3ImageUrl = row['Headshot']

                    print (athlete)
                    athlete.save()
                    url = 'AIS_PROJ/media/%s_%s.jpg' % (athlete.name, athlete.id)
                    if not os.path.isfile(url):
                        f = open(url, 'wb')
                        f.write(requests.get(athlete.s3ImageUrl).content)
                        f.close()
                    print ('uploading to s3...')
                    file = open(url, 'rb')
                    key = "%s_%s.jpg" % (athlete.name, athlete.id)
                    object = s3.Object(bucket, key)
                    object.put(Body=file, ContentType='image/jpeg', ACL='public-read',
                               Metadata={'fullname': athlete.name, 'athlete_id': athlete.id})

            print ('Adding events...')
            for row in csv_dicts:
                print (row['EventID'])
                print (row['ID'])
                event = Event.objects.filter(id=row['EventID'])
                print (event)
                if not event:
                    event = Event()
                    event.name = row['Event']
                    event.id = row['EventID']
                    event.athletes.add(row['ID'])
                    event.save()
                else:
                    event = event.all()[:1].get()
                    athleteInEvent = event.athletes.filter(id=row['ID'])
                    if not athleteInEvent:
                        event.athletes.add(row['ID'])
                        event.save()
            return redirect('index')

        except:
            print ('Error in csv format')

    return render(request, 'import_form.html')


@login_required
def index(request):
    title = "Athletes"
    athletes = Athlete.objects.filter(is_provider=False)
    return render(request, "athletes/index.html", {"title": title, 'athletes': athletes})


@login_required
def get_participentes(request, pk):
    title = "Athletes"
    event = get_object_or_404(Event, pk=pk)
    athletes = event.athletes.all()
    # athletes = Athlete.objects.all()
    return render(request, "athletes/index.html",
                  {"heading": event.name, 'event': event, "title": title, 'athletes': athletes})


@login_required
def create(request):
    title = 'Create Athlete'
    imageErr = ''
    if request.method == 'POST':
        form = AthleteCreationForm(request.POST, request.FILES)
        if form.is_valid():
            image = face_recognition.load_image_file(request.FILES.get('image'))
            enc = face_recognition.face_encodings(image)
            noOfFaces = enc.__len__()
            print (noOfFaces)
            if noOfFaces == 1:
                form.save()
                return redirect('index')
            else:
                imageErr = "The Image has %s faces in it\n Please upload image with only one face in it." % noOfFaces
    else:
        form = AthleteCreationForm()
    return render(request, 'athletes/create.html', {'form': form, 'title': title, 'imageErr': imageErr})


@login_required
def update(request, pk):
    user = request.user
    next_url = request.GET.get('next')
    athlete = Athlete.objects.get(pk=pk)
    title = "Update " + athlete.name
    imageErr = ''
    if request.method == 'POST':
        form = AthleteCreationForm(request.POST, request.FILES, instance=athlete)
        if form.is_valid():
            if request.FILES.__len__() != 0:
                image = face_recognition.load_image_file(request.FILES.get('image'))
                enc = face_recognition.face_encodings(image)
                noOfFaces = enc.__len__()
                if noOfFaces == 1:
                    form.save()
                    id = str(athlete.id)  # type: str
                    key = "%s_%s_%s.jpg" % (user.username, athlete.id, athlete.image)
                    url = "AIS_PROJ/%s" % athlete.image.url
                    file = open(url, 'rb')
                    object = s3.Object(bucket, key)
                    object.put(Body=file, ContentType='image/jpeg', ACL='public-read',
                               Metadata={'fullname': athlete.name, 'athlete_id': id})
                    s3Url = "https://s3.amazonaws.com/%s/%s" % (bucket, key)
                    athlete.s3ImageUrl = s3Url
                    request.session['image'] = athlete.s3ImageUrl
                    athlete.save()
                    path_to_file = '%s/%s' % (settings.BASE_DIR, url)
                    print (path_to_file)
                    if os.path.exists(path_to_file):
                        os.remove(path_to_file)
                    if next_url:
                        return redirect(next_url)
                    return redirect('/events')
                else:
                    imageErr = "The Image has %s faces in it\n Please upload image with only one face in it." % noOfFaces
            else:
                form.save()
                athlete.profile_complete = True
                athlete.save()
                if next_url:
                    return redirect(next_url)
                return redirect('index')
    else:
        form = AthleteCreationForm(instance=athlete)
    return render(request, 'athletes/create.html',
                  {'form': form, 'title': title, 'imageErr': imageErr, 's3ImageUrl': athlete.s3ImageUrl})


@login_required
def delete(request, pk):
    athlete = Athlete.objects.get(pk=pk)
    title = 'Delete ' + athlete.name
    if request.method == 'POST':
        athlete.delete()
        return redirect('index')
    else:
        return render(request, 'delete_form.html', {'title': title, 'object': athlete.name})


@login_required
def athlete_gallery(request, pk):
    try:
        athlete = Athlete.objects.get(pk=pk)
    except Athlete.DoesNotExist:
        user = request.user

        athlete = get_object_or_404(Athlete, user=user)

    title = "%s Gallery" % athlete.name
    s3Images = athlete.s3images_set.all()
    print(s3Images)
    url = '#'
    if request.method == 'POST':
        athleteID = request.POST['event']
        eventID = request.POST['athlete']
        fileKey = 'AthletesResults/A%s_E%s.zip' % (athleteID, eventID)
        print("Bucket")
        print(BUCKET)
        url = s3Client.generate_presigned_url('get_object',
                                              Params={
                                                  'Bucket': BUCKET,
                                                  'Key': fileKey,
                                              },
                                              ExpiresIn=3600,
                                              HttpMethod='get')
        print (url)
    return render(request, 'gallary.html', {'title': title, 'data': athlete, 'data_type': 'athlete',
                                            'images': s3Images, 'url': url, 'imagecount': s3Images.__len__()})


@login_required
def stats(request, pk):
    athelete = Athlete.objects.get(pk=pk)
    title = "%s images" % athelete.name
    events = athelete.event_set.all()
    data = []
    for event in events:
        images = event.s3images_set.all()
        images = images.filter(athlete_id=athelete.id)
        d = {'xData': event.name, 'yData': images.__len__()}
        data.append(d)
    json_data = json.dumps(data)
    return render(request, 'graph.html', {'json_data': json_data, 'title': title})


@login_required
def profile_update(request):
    try:
        athlete = Athlete.objects.get(user=request.user)
    except Athlete.DoesNotExist:
        athlete = Athlete.objects.create(user=request.user)
    return redirect('update-athlete', pk=athlete.pk)


@login_required
def participated(request):
    athlete = Athlete.objects.get(user=request.user)
    events = athlete.event_set.all()
    context = {
        'events': events,
        'title': 'My participated projects'
    }
    return render(request, 'athletes/participated_events.html', context=context)


@login_required
def get_task_status(request, pk):
    athlete = Athlete.objects.get(user=request.user)
    event = athlete.event_set.get(pk=pk)
    task = Task.objects.filter(athlete=athlete, event=event).last()
    data = dict()
    if task:
        data['task_id'] = task.pk
        data['task_status'] = task.status
    return JsonResponse(data=data, safe=False)
