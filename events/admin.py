from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Event)
admin.site.register(s3Images)
admin.site.register(Logs)
admin.site.register(ScanLog)
admin.site.register(EventImage)
admin.site.register(ScanQueue)
admin.site.register(Task)
admin.site.register(PicLog)
