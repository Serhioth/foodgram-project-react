from django import forms
from django.contrib import admin
from django.contrib.admin import display

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag


class RecipeAddForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ('author',
                  'ingredients',
                  'tags',
                  'name',
                  'image',
                  'text',
                  'cooking_time')


class RecipeChangeForm(forms.ModelForm):
    model = Recipe
    fields = '__all__'


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
    list_filter = ('tags',)
    search_fields = ('author__username', 'author__email')
    inlines = (IngredientAmountInline, )

    @display(description='Favorited')
    def added_in_favorites(self, obj):
        return obj.favorited.all().count()

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            kwargs['form'] = RecipeChangeForm
        else:
            kwargs['form'] = RecipeAddForm
        return super().get_form(request, obj, **kwargs)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug',)


@admin.register(IngredientAmount)
class IngrdientAmount(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount',)
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('ingredient__measurement_unit', 'recipe__tags')
