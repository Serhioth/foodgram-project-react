import base64

import webcolors
from django.core.files.base import ContentFile
from rest_framework import serializers

from foodgram.settings import MIN_INGREDIENTS, MAX_INGREDIENTS
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
    name = serializers.CharField(max_length=200)
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True)
    cooking_time = serializers.IntegerField()
    ingredients = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('author', 'name'),
                message='У Вас может быть только один рецепт с таким названием'
            ),
        )
        fields = '__all__'

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.all()
        num_of_ingredients = ingredients.count()

        if num_of_ingredients <= MIN_INGREDIENTS:
            raise serializers.ValidationError(
                'Рецепт должен содержать хотя бы '
                f'{MIN_INGREDIENTS} ингредиента'
            )
        elif num_of_ingredients >= MAX_INGREDIENTS:
            raise serializers.ValidationError(
                'Рецепт не может содержать '
                f'больше чем {MAX_INGREDIENTS}'
                'ингредиентов'
            )

        ingredient_ids = [ingredient.id for ingredient in ingredients]
        if len(ingredient_ids) != num_of_ingredients:
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться!'
            )

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

    def validate_cooking_time(self, value):
        if 0 <= value <= 720:
            return value
        return serializers.ValidationError(
            'Время готовки не может быть меньше нуля, '
            'если на приготовление Вашего рецепта '
            'действительно нужно больше 12 часов - '
            'обратитесь к администрации сайта',
        )
