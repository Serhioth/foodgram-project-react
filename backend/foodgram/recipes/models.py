from django.contrib import auth
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from foodgram.settings import (MIN_COOKING_TIME,
                               MAX_COOKING_TIME,
                               MIN_AMOUNT,
                               MAX_AMOUNT)

User = auth.get_user_model()


class Ingredient(models.Model):
    """Model for ingredients"""
    name = models.CharField(
        'Ingredient name',
        max_length=50,
        help_text='Ingredient name'
    )
    measurement_unit = models.CharField(
        'Measurement unit',
        max_length=30,
        help_text='Measurement unit'
    )

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    """Model for tags"""
    name = models.CharField(
        'Tag name',
        max_length=30,
        help_text='Tag'
    )
    color = models.CharField(
        'Tag color',
        max_length=16,
        help_text='Color'
    )
    slug = models.SlugField(
        'Tag slug',
        max_length=30,
        unique=True,
        help_text='Slug'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'color'),
                name='unique_name_color'
            ),
        )

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    """Model for recipes"""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        help_text='user recipes'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        help_text='Ingredients'
    )
    favorited = models.ManyToManyField(
        'users.User',
        blank=True,
        related_name='favorited_recipes',
        help_text='Favorited by'
    )
    in_shopping_cart = models.ManyToManyField(
        'users.User',
        blank=True,
        related_name='shopping_cart',
        help_text='Users added to cart'
    )
    tags = models.ManyToManyField(
        'recipes.Tag',
        blank=True,
        related_name='tagged_recipes',
        help_text='Recipes tags'
    )
    name = models.CharField(
        'Recipe Name',
        max_length=200,
        help_text='Name'
    )
    image = models.ImageField(
        upload_to='recipes/images',
        null=True,
        default=None
    )
    text = models.TextField(
        'Recipe description'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Time of cooking',
        validators=(
            MinValueValidator(
                limit_value=MIN_COOKING_TIME,
                message='Cooking time should not be '
                        f'less than {MIN_COOKING_TIME}.'
            ),
            MaxValueValidator(
                limit_value=MAX_COOKING_TIME,
                message='Cooking time should not be '
                        f'more than {MAX_COOKING_TIME}.'
            )
        ),
        help_text='Time of cooking'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_recipe_name_author'
            ),
        )


class IngredientAmount(models.Model):
    """Model for ingredients"""
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        'Amount of ingredient',
        validators=(
            MinValueValidator(
                limit_value=MIN_AMOUNT,
                message='Amount of ingredient should not be '
                        f'less than {MIN_AMOUNT}.'
            ),
            MaxValueValidator(
                limit_value=MAX_AMOUNT,
                message='Amount of ingredient should not be '
                        f'more than {MAX_AMOUNT}.'
            )
        ),
        help_text='Amount',
    )

    def __str__(self) -> str:
        return f'{self.ingredient.name}: {self.amount}'
