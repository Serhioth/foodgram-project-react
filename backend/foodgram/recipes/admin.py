from django.contrib import admin

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    fields = ('ingredient', 'amount', 'ingredient_measurement_unit')
    readonly_fields = ('ingredient_measurement_unit',)
    extra = 0

    def ingredient_measurement_unit(self, instance):
        return instance.ingredient.measurement_unit

    ingredient_measurement_unit.short_description = 'unit'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    inlines = (IngredientAmountInline, )


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(IngredientAmount)
