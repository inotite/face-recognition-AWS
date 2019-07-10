# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Manager

from events.models import Event


class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dropbox_token = models.CharField(max_length=500, null=True)
    projects = models.ManyToManyField(Event)
    users = models.ManyToManyField(User, related_name='project_users')  # type: Manager
