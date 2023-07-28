import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Recipe

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """Custom field to convert images to Base64 byte strings"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserRecipeSerializer(serializers.ModelSerializer):
    """This serializer is necessary to prevent recircular import"""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, object):

        return object.username in self.context.get(
            'request',
            None
        ).user.get_subscribes()


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions"""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, object):
        limit = self.context.get('limit', None)
        if limit:
            recipes = object.recipes.all()[:limit]
        else:
            recipes = object.recipes.all()
        recipes = UserRecipeSerializer(
            recipes,
            many=True
        )
        return recipes.data

    def get_recipes_count(self, object):
        return object.recipes.all().count()
