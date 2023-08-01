import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
import webcolors


class Hex2NameColor(serializers.Field):
    """Class to represent HEXCode to color name"""
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('No title for such color.')
        return data


class Base64ImageField(serializers.ImageField):
    """Custom field to convert image to Base64 byte-string"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)
