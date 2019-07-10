from django.db import models
from athletes.models import Athlete
from django.contrib.auth.models import User


class EventImage(models.Model):
    link = models.CharField(max_length=500, null=False)
    name = models.CharField(max_length=100, null=True)
    dbx_path = models.CharField(max_length=500, null=True)


class Event(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    dropbox_Folder = models.CharField(max_length=500, null=True, blank=True)
    athletes = models.ManyToManyField(Athlete)
    is_s3_active = models.BooleanField(default=False)
    status = models.CharField(default='NotProcessed', max_length=30, null=True)
    dbx_link = models.CharField(max_length=500, null=True, blank=True)
    threshold = models.IntegerField(null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    image_links = models.ManyToManyField(EventImage)

    def __str__(self):
        return self.name


class s3Images(models.Model):
    s3Url = models.CharField(max_length=500)
    dropbox_Url = models.CharField(max_length=600, null=True)
    event = models.ForeignKey(Event, null=True, on_delete=models.CASCADE)
    athlete = models.ManyToManyField(Athlete)

    def __str__(self):
        return self.dropbox_Url


class Logs(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)

    def __str__(self):
        return "%s___%s " % (self.event, self.athlete)


class ScanLog(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    dropbox_images = models.IntegerField(null=False)
    athletes = models.IntegerField(null=False)
    time_taken = models.FloatField(null=True)
    athlete = models.ForeignKey(Athlete, on_delete=models.SET_NULL, null=True)
    time_of_completion = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        try:
            return "Project: %s ___ Dropbox Images: %s ___ Person: %s ___ Scan Time: %s min__Completed on: %s" % \
                   (self.event.name, self.dropbox_images, self.athlete.name, self.time_taken / 60,
                    str(self.time_of_completion))
        except:
            return 'Effected Log'


class ScanQueue(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    is_scanned = models.BooleanField(default=False)


class Task(models.Model):
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)

    def __str__(self):
        return "Event: %s --- Athlete: %s" % (self.event.name, self.athlete.name)


class PicLog(models.Model):
    pic_link = models.CharField(max_length=200, null=False)
    athlete = models.ForeignKey(Athlete, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_person_found = models.BooleanField(default=False)
    comment = models.TextField(max_length=200, null=True)

    def __str__(self):
        try:
            return "%s   -   %s  -   %s   -  %s" % (
            self.pic_link, self.athlete.name, self.event.name, str(self.is_person_found))
        except:
            return self.pic_link
