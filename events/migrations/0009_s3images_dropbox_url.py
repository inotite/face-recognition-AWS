# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-09-19 12:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0008_logs'),
    ]

    operations = [
        migrations.AddField(
            model_name='s3images',
            name='dropbox_Url',
            field=models.CharField(max_length=600, null=True),
        ),
    ]