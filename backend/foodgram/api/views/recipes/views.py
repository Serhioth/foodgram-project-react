from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.serializers.recipes.filters import IngredientFilter, RecipeFilter
from api.serializers.recipes.permissions import (IsAdminOrReadOnly,
                                                 IsAuthorOrReadOnly)
from api.serializers.recipes.renderers import PdfRenderer
from api.serializers.recipes.serializers import (CreateRecipeSerializer,
                                                 IngredientSerializer,
                                                 TagSerializer)
from api.serializers.recipes.renderers import CONTENT_TYPE
from recipes.models import Ingredient, Recipe, Tag

DATE_FORMAT = '%Y-%m-%d'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Ingredient model viewset. """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Tag model viewset. """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for /recipes, /shopping_cart and /favorites. """
    permission_classes = (
        IsAuthorOrReadOnly | IsAdminOrReadOnly,
    )
    queryset = Recipe.objects.all()
    serializer_class = CreateRecipeSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = RecipeFilter
    ordering_fields = ('created_at', 'updated_at')
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(
        methods=('GET', ),
        renderer_classes=(PdfRenderer, ),
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        now = timezone.now()
        time = now.strftime(DATE_FORMAT)
        pdf_data = {
            'user': request.user,
        }
        response = HttpResponse(
            content_type=CONTENT_TYPE,
            headers={
                'Content-Disposition': ('attachment; '
                                        'filename="shopping_list'
                                        f'_{time}_'
                                        f'{request.user.username}.pdf"')}
        )
        response.write(PdfRenderer().render(pdf_data))
        return response

    @action(
        methods=('POST', 'DELETE'),
        url_path='shopping_cart',
        detail=True,
        permission_classes=(IsAuthenticated, )
    )
    def add_to_shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if recipe in user.shopping_cart.all():
                return Response(
                    {'message': 'Recipe already in shopping cart.'}
                )

            user.shopping_cart.add(recipe)

            return Response(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': str(bytes(recipe.image.read())),
                    'cooking_time': recipe.cooking_time
                },
                status=status.HTTP_201_CREATED
            )

        if recipe not in user.shopping_cart.all():
            return Response(
                {'message': 'Not in shopping cart.'}
            )

        request.user.shopping_cart.remove(recipe)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=('POST', 'DELETE'),
        detail=True,
        url_path='favorite',
        permission_classes=(IsAuthenticated, )
    )
    def favorites(self, request, pk=None):

        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if recipe in user.favorited_recipes.all():
                return Response(
                    {'message': 'Already in your favorites.'}
                )

            user.favorited_recipes.add(recipe)

            return Response(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': recipe.image.read().decode(),
                    'cooking_time': recipe.cooking_time
                },
                status=status.HTTP_201_CREATED
            )

        if recipe not in user.favorited_recipes.all():
            return Response(
                {'message': 'Not favorited.'}
            )

        user.favorited_recipes.remove(recipe)

        return Response(status=status.HTTP_204_NO_CONTENT)
