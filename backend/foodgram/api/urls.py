from api.views.users.views import CustomUserViewSet
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter

from api.views.recipes.views import (IngredientViewSet,
                                     RecipeViewSet,
                                     TagViewSet)

app_name = 'api'

router = DefaultRouter()

router.register(
    r'users',
    CustomUserViewSet,
    basename='CustomUser-viewset'
)
router.register(
    r'recipes',
    RecipeViewSet,
    basename='Recipe-viewset'
)
router.register(
    r'tags',
    TagViewSet,
    basename='Tag-viewset'
)
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='Ingredient-viewset'
)

urlpatterns = [
    path('', include(router.urls)),
    path('docs/', TemplateView.as_view()),
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken'))
]
