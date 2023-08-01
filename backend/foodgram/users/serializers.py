from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Recipe
from recipes.serializer_fields import Base64ImageField

User = get_user_model()


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
