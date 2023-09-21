from api.serializers.recipes.serializer_fields import Base64ImageField
from api.serializers.users.serializers import UserSerializer
from foodgram.settings import (MAX_AMOUNT, MAX_COOKING_TIME, MAX_INGREDIENTS,
                               MAX_TAGS, MIN_AMOUNT, MIN_COOKING_TIME,
                               MIN_INGREDIENTS, MIN_TAGS)
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from rest_framework import serializers


class TagSerializer(serializers.ModelSerializer):
    """Tag model serializer. """

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient model serializer. """

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient',
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < MIN_AMOUNT or value > MAX_AMOUNT:
            raise serializers.ValidationError(
                f"Amount of ingredient should not be less than {MIN_AMOUNT} "
                f"and more than {MAX_AMOUNT}."
            )
        return value


class IngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Serializer to represent ingredients in recipe"""
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer to represent Recipe objects. """
    image = Base64ImageField()
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_ingredients(self, recipe):
        ingredients = IngredientAmount.objects.filter(recipe=recipe)
        return IngredientsInRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, recipe):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return recipe in request.user.favorited_recipes.all()

    def get_is_in_shopping_cart(self, recipe):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return recipe in request.user.shopping_cart.all()


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Serializer for create recipe objects. """
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    author = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    ingredients = IngredientAmountSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe

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
        validators = (
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('author', 'name'),
                message='You can have only one recipe with such title.'
            ),
        )

    def validate_ingredients(self, value):
        if not value:
            raise serializers.ValidationError(
                'At least one ingredient is required.'
            )

        ingredient_ids = {ingredient['ingredient'].id for ingredient in value}
        unique_ingredient_ids = len(ingredient_ids)
        total_ingredient_ids = len(value)

        if unique_ingredient_ids != total_ingredient_ids:
            raise serializers.ValidationError(
                'Each ingredient must be unique. '
                'Repeated ingredients are not allowed.'
            )
        if (
            unique_ingredient_ids < MIN_INGREDIENTS
            or MAX_INGREDIENTS < unique_ingredient_ids
        ):
            raise serializers.ValidationError(
                'Number of ingredients must '
                f'be more then {MIN_INGREDIENTS}'
                f' and less then {MAX_INGREDIENTS}.'
            )

        if unique_ingredient_ids != total_ingredient_ids:
            raise serializers.ValidationError(
                'Each ingredient must be unique. '
                'Repeated ingredients are not allowed.'
            )

        if not Ingredient.objects.filter(
            pk__in=ingredient_ids
        ).count() == unique_ingredient_ids:
            raise serializers.ValidationError(
                'Invalid ingredient ID(s) provided.'
            )

        return value

    def validate_tags(self, value):
        tags = value
        num_of_tags = len(value)

        if num_of_tags < MIN_TAGS:
            raise serializers.ValidationError(
                'Recipe should have '
                f'at least {MIN_TAGS} tag(s).'
            )
        if num_of_tags > MAX_TAGS:
            raise serializers.ValidationError(
                'Recipe should not have '
                f'more than {MAX_TAGS} tag(s).'
            )

        tag_ids = [tag.id for tag in tags]
        if len(set(tag_ids)) != num_of_tags:
            raise serializers.ValidationError(
                'Tags should not be repeated.'
            )

        return tags

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

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop("ingredients")

        request = self.context.get('request')
        validated_data['author'] = request.user

        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            IngredientAmount.objects.create(recipe=recipe, **ingredient_data)
        for tag in tags_data:
            recipe.tags.add(tag)

        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)

        if 'tags' in validated_data:
            instance.tags.set([])
            for tag_data in validated_data.pop('tags'):
                instance.tags.add(tag_data)

        if 'ingredients' in validated_data:
            IngredientAmount.objects.filter(
                recipe=instance
            ).delete()

            ingredients_data = validated_data.pop('ingredients')
            for ingredient in ingredients_data:
                ingredient_instance = Ingredient.objects.get(
                    id=ingredient['id']
                )
                instance.ingredients.add(
                    ingredient_instance,
                    through_defaults={'amount': ingredient['amount']}
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
