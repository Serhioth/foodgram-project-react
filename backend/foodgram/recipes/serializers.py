from rest_framework import serializers

from foodgram.settings import (MIN_INGREDIENTS,
                               MAX_INGREDIENTS,
                               MIN_COOKING_TIME,
                               MAX_COOKING_TIME,
                               MIN_AMOUNT,
                               MAX_AMOUNT)
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from recipes.serializer_fields import Hex2NameColor, Base64ImageField
from users.serializers import UserSerializer


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
                message='You can have only one recipe with such title.'
            ),
        )
        fields = '__all__'

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.all()
        num_of_ingredients = ingredients.count()

        if num_of_ingredients <= MIN_INGREDIENTS:
            raise serializers.ValidationError(
                'Recipe must contain  at least '
                f'{MIN_INGREDIENTS} ingredients.'
            )
        if num_of_ingredients >= MAX_INGREDIENTS:
            raise serializers.ValidationError(
                'Recipe must contain '
                f'no more than {MAX_INGREDIENTS} '
                'ingredients.'
            )

        ingredient_ids = [ingredient.id for ingredient in ingredients]
        if len(ingredient_ids) != num_of_ingredients:
            raise serializers.ValidationError(
                'Ingredients should not be repeated.'
            )

        serialized_ingredients = IngredientSerializer(
            ingredients,
            many=True
        ).data
        for i, ingredient in enumerate(ingredients):
            amount = IngredientAmount.objects.get(
                recipe=recipe,
                ingredient=ingredient
            ).amount
            if MIN_AMOUNT <= amount <= MAX_AMOUNT:
                raise serializers.ValidationError(
                    f'Amount of ingredient {ingredient.name} '
                    f'should not be less than {MIN_AMOUNT} '
                    f'and more then {MAX_AMOUNT}.'
                )
            serialized_ingredients[i]['amount'] = amount
        return serialized_ingredients

    def validate_cooking_time(self, value):
        if MIN_COOKING_TIME <= value <= MAX_COOKING_TIME:
            return value
        return serializers.ValidationError(
            'Time of cooking should not be, '
            f'less than {MIN_COOKING_TIME}. '
            'If cooking of your dishes'
            f'require more time than {MAX_COOKING_TIME}'
            'please contact site administration.',
        )
