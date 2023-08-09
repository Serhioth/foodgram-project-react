from django.db import transaction
from rest_framework import serializers

from foodgram.settings import (MIN_INGREDIENTS,
                               MAX_INGREDIENTS,
                               MIN_COOKING_TIME,
                               MAX_COOKING_TIME,
                               MIN_AMOUNT,
                               MAX_AMOUNT,
                               MIN_TAGS,
                               MAX_TAGS)
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
    id = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


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
        fields = '__all__'

    def get_ingredients(self, recipe):
        ingredients = recipe.ingredients.all()

        serialized_ingredients = IngredientSerializer(
            ingredients,
            many=True
        ).data
        for i, ingredient in enumerate(ingredients):
            amount = IngredientAmount.objects.get(
                recipe=recipe,
                ingredient=ingredient
            ).amount
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


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Serializer for create recipe objects"""
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )
        model = Recipe
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('author', 'name'),
                message='You can have only one recipe with such title.'
            ),
        )

    def validate_ingredients(self, value):
        ingredients = value
        num_of_ingredients = ingredients.count()

        if MIN_INGREDIENTS <= num_of_ingredients:
            raise serializers.ValidationError(
                'Recipe must contain  at least '
                f'{MIN_INGREDIENTS} ingredients.'
            )
        if MAX_INGREDIENTS <= num_of_ingredients:
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

        for ingredient in ingredients:
            if MIN_AMOUNT <= ingredient.amount:
                raise serializers.ValidationError(
                    f'Amount of ingredient {ingredient.name} '
                    f'should not be less than {MIN_AMOUNT}.'
                )
            if MAX_AMOUNT <= ingredient.amount:
                raise serializers.ValidationError(
                    f'Amount of ingredient {ingredient.name} '
                    f'should not be more than {MAX_AMOUNT}.'
                )

    def validate_tags(self, value):
        tags = value
        num_of_tags = tags.count()

        if num_of_tags <= MIN_TAGS:
            raise serializers.ValidationError(
                'Recipe should have '
                f'at least {MIN_TAGS}.'
            )
        if num_of_tags >= MAX_TAGS:
            raise serializers.ValidationError(
                'Recipe should not have '
                f'more than {MAX_TAGS}.'
            )

        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != num_of_tags:
            raise serializers.ValidationError(
                'Tags should not be repeated.'
            )

    @transaction.atomic
    def create_ingredients_amounts(self, ingredients, recipe):
        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        self.create_ingredients_amounts(
            recipe=recipe,
            ingredients=ingredients
        )

        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()

        self.create_ingredients_amounts(
            recipe=instance,
            ingredients=ingredients
        )

        instance.save()
        return instance

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance,
            context=context
        ).data
