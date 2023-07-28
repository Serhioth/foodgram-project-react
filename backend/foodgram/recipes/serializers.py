import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.serializers import UserSerializer


class Hex2NameColor(serializers.Field):
    """Class to represent HEXCode to color name"""
    def to_representation(self, value):
        return value

    def to_internal_value(self, data):
        try:
            data = webcolors.hex_to_name(data)
        except ValueError:
            raise serializers.ValidationError('Для этого цвета нет имени')
        return data


class Base64ImageField(serializers.ImageField):
    """Custom field to convert image to Base64 byte-string"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Tag model serializer"""
    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient model serializer"""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Ingredient amount serializer"""
    class Meta:
        model = IngredientAmount
        fields = ('amount', )


class RecipeSerializer(serializers.ModelSerializer):
    """Recipe model serializer"""
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.all()
        serialized_ingredients = IngredientSerializer(
            ingredients,
            many=True
        ).data
        for i, ingredient in enumerate(ingredients):
            serialized_ingredients[i]['amount'] = IngredientAmount.objects.get(
                recipe=recipe,
                ingredient=ingredient
            ).amount
        return serialized_ingredients
