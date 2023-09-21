from django.contrib.auth import get_user_model
from rest_framework import serializers

from recipes.models import Recipe
from api.serializers.recipes.serializer_fields import Base64ImageField
from api.serializers.users.validators import (check_user_is_not_registred,
                                              check_username)

User = get_user_model()


class UserRecipeSerializer(serializers.ModelSerializer):
    """This serializer is necessary to prevent recircular import. """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model. """
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
            'password'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'is_subscribed': {'read_only': True}
        }

    def validate_username(self, value):
        """Checking that the username meets the registration requirements. """
        if not check_username(value):
            raise serializers.ValidationError(
                {'message':
                    'The username should not be Me, '
                    'contains invalid characters, '
                    'or exceeds the allowed length of 150 characters'}
            )
        return value

    def validate(self, attrs):
        """
       Checking that user does not
       register with already taken mailbox or usename.
        """
        email = attrs.get('email')
        username = attrs.get('username')
        if not check_user_is_not_registred(
            email=email,
            username=username
        ):
            raise serializers.ValidationError(
                {'message':
                 f'User with such username - {username} '
                 f'or mailbox - {email} allready registred'}
            )
        return super().validate(attrs)

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def get_is_subscribed(self, object):

        return object.username in self.context.get(
            'request',
            None
        ).user.get_subscribes()


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Serializer for subscriptions. """
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
        limit = self.context.get('recipes_limit', None)
        if limit and limit.isdigit():
            recipes = object.recipes.all()[:int(limit)]
        else:
            recipes = object.recipes.all()
        recipes = UserRecipeSerializer(
            recipes,
            many=True
        )
        return recipes.data

    def get_recipes_count(self, object):
        return object.recipes.all().count()
