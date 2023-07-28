from django.urls import include, path
from rest_framework.routers import SimpleRouter

from recipes.views import RecipeViewSet, TagViewSet
from users.views import CustomUserViewSet

app_name = 'api'

router = SimpleRouter()

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

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken'))
]
