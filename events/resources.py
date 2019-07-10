from import_export import resources
from .models import s3Images


class EventResource(resources.ModelResource):
    class Meta:
        model = s3Images
        fields = ('athlete.name', 'dropbox_Url','event.name')