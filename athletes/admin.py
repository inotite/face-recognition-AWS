from django.contrib import admin
from .models import Athlete
from .resources import AthleteResource
from import_export.admin import ImportExportModelAdmin
# Register your models here.


@admin.register(Athlete)
class PersonAdmin(ImportExportModelAdmin):
    pass

