from django.contrib import admin
from django.contrib.admin import display

from .models import Ingredient, IngredientAmount, Recipe, Tag


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    fields = ('ingredient', 'amount', 'ingredient_measurement_unit')
    readonly_fields = ('ingredient_measurement_unit',)
    extra = 0

    def ingredient_measurement_unit(self, instance):
        return instance.ingredient.measurement_unit

    ingredient_measurement_unit.short_description = 'unit'


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'author')
    list_filter = ('author', 'name', 'tags',)
    inlines = (IngredientAmountInline, )

    @display(description='Favorited')
    def added_in_favorites(self, obj):
        return obj.favorited.all().count()


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    list_filter = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(IngredientAmount)
class IngrdientAmount(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
