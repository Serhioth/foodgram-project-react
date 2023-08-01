from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.serializers import SubscriptionsSerializer, UserSerializer

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    User model view-set,
    support work with subscriptions endpoints
    """
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (SearchFilter, )
    search_fields = ('name', )

    @action(
        methods=('GET', ),
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated, )
    )
    def get_subscribes(self, request):
        queryset = request.user.subscribes.all()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={'request': request}
            )
            return self.get_paginated_response(
                serializer.data
            )
        return Response(
            data=queryset.data,
            status=HTTPStatus.OK
        )

    @action(
        detail=True,
        methods=('POST', 'DELETE'),
        url_path='subscribe',
        permission_classes=(IsAuthenticated, )
    )
    def edit_subscribes(self, request, pk=None):
        user = request.user
        subscribe = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            if subscribe in user.subscribes.all():
                return Response(
                    {'message': 'Already subscribed.'}
                )
            user.subscribes.add(subscribe)
            serializer = SubscriptionsSerializer(
                subscribe,
                context={
                    'request': request,
                }
            )
            return Response(
                serializer.data, status=HTTPStatus.CREATED
            )

        if subscribe not in user.subscribes.all():
            return Response(
                {'message': 'Not subscribed.'}
            )

        user.subscribes.remove(subscribe)
        return Response(status=HTTPStatus.NO_CONTENT)
