from rest_framework import serializers
from .models import s3Images


class s3ImagesSerialize(serializers.ModelSerializer):
    athletes = serializers.SerializerMethodField()

    def get_athletes(self, s3Image):
        return ', '.join([str(athlete) for athlete in s3Image.athlete.all()])

    class Meta:
        model = s3Images
        fields = (
            's3Url',
            'athletes',
            'event',
            'id'
        )
