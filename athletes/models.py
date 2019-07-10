from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Athlete(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=50, null=False, blank=False)
    image = models.ImageField('Athletes/Images', null=False, blank=False)
    s3ImageUrl = models.CharField(max_length=600, blank=True, null=True)
    is_provider = models.BooleanField(default=False)
    profile_complete = models.BooleanField(default=False)

    def __str__(self):
        return self.name


