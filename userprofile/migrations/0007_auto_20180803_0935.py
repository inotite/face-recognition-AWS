# Generated by Django 2.0.7 on 2018-08-03 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0006_auto_20180801_1212'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]