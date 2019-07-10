from import_export import resources
from .models import Athlete


class AthleteResource(resources.ModelResource):
    class Meta:
        model = Athlete
        fields = ('name', 's3ImageUrl')