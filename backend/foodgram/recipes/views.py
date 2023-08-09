import dotenv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response

from recipes.filters import RecipeFilter, IngredientFilter
from recipes.models import Recipe, Tag, Ingredient
from recipes.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from recipes.renderers import PdfRenderer
from recipes.serializers import (RecipeSerializer,
                                 CreateRecipeSerializer,
                                 TagSerializer,
                                 IngredientSerializer)

dotenv.load_dotenv()
CONTENT_TYPE = 'application/pdf'


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for /recipes, /shopping_cart and /favorites"""
    permission_classes = (
        IsAuthorOrReadOnly | IsAdminOrReadOnly
    )
    queryset = Recipe.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filter_class = RecipeFilter
    ordering_fields = ('created_at', 'updated_at')
    http_method_names = ('get', 'post', 'patch', 'delete')

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return CreateRecipeSerializer

    @action(
        methods=('GET', ),
        renderer_classes=(PdfRenderer, ),
        url_path='download_shopping_cart',
        detail=False,
        permission_classes=(IsAuthenticated, )
    )
    def download_shopping_cart(self, request):
        now = timezone.now()
        time = now.strftime('%Y-%m-%d')
        pdf_data = {
            'user': request.user,
        }
        response = HttpResponse(
            content_type=CONTENT_TYPE,
            headers={
                'Content-Disposition':
                    'attachment; '
                    'filename="shopping_list'
                    f'_{time}_{request.user.username}.pdf"'}
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
                    'image': recipe.image,
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
        methods=('POST', 'DEL'),
        detail=True,
        url_path='favorite',
        permission_classes=(IsAuthenticated, )
    )
    def favorites(self, request, pk=None):

        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user

        if request.method == 'POST':
            if recipe in user.favorited.recipes.all():
                return Response(
                    {'message': 'Already in your favorites.'}
                )

            user.favorited_recipes.add(recipe)

            return Response(
                {
                    'id': recipe.id,
                    'name': recipe.name,
                    'image': str(bytes(recipe.image.read())),
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
