from django.urls import include, path
from recipes.views import IngredientViewSet, RecipeViewSet, TagViewSet
from rest_framework.routers import DefaultRouter
from users.views import CustomUserViewSet

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
    path('', include('djoser.urls')),
    path(r'auth/', include('djoser.urls.authtoken'))
]
