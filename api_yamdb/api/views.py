from django.db import IntegrityError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .filter import TitleFilter
from .permissions import (AdminOrReadOnly,
                          AdminOrModeratorOrAuthor,
                          AdminOrMyselfOnly)
from .serializers import (CategoriesSerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer,
                          RegisterSerializer, ReviewSerializer,
                          TitleSerializer, UserSerializer)
from .utils import create_and_send_code
from api_yamdb.settings import (ERR_USERNAME_EXISTS,
                                ERR_EMAIL_EXISTS)
from reviews.models import Category, Genre, Review, Title
from users.models import User


class CreateDestroyListViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    permission_classes = (AdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('slug', 'name')
    lookup_field = 'slug'


class TitleListView(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).all()
    serializer_class = TitleSerializer
    permission_classes = (AdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleFilter
    ordering_fields = ('id', )


class GenreListView(CreateDestroyListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoriesListView(CreateDestroyListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (AdminOrModeratorOrAuthor,)

    def get_queryset(self):
        return get_object_or_404(
            Title, pk=self.kwargs.get('title_id')
        ).reviews.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            title=get_object_or_404(
                Title, pk=self.kwargs.get('title_id')
            )
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (AdminOrModeratorOrAuthor,)

    def get_queryset(self):
        return get_object_or_404(
            Review, pk=self.kwargs.get('review_id')
        ).comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            review=get_object_or_404(
                Review, pk=self.kwargs.get('review_id'))
        )


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для пользователя с эндпоинтом /me."""

    queryset = User.objects.all()
    permission_classes = [AdminOrMyselfOnly]
    serializer_class = UserSerializer
    lookup_field = 'username'

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=[IsAuthenticated],
        url_path='me',
        url_name='me'
    )
    def retrieve_patch_me(self, request):
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterUserAPIView(APIView):
    """Регистрация пользователя и получение кода подтверждения."""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, created = User.objects.get_or_create(
                **serializer.validated_data
            )
        except IntegrityError:
            email = serializer.validated_data.get('email')
            error = (
                ERR_EMAIL_EXISTS if User.objects.filter(email=email).exists()
                else ERR_USERNAME_EXISTS
            )
            return Response(
                {'Ошибка': error},
                status=status.HTTP_400_BAD_REQUEST
            )
        create_and_send_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ObtainTokenView(APIView):
    """Получение токена авторизации."""

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        if not user.confirmation_code:
            return Response(
                {'Ошибка': 'Для получения токена пройдите авторизацию.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        refresh = RefreshToken.for_user(user)
        token = {'token': str(refresh.access_token)}
        user.confirmation_code = ''
        user.save(update_fields=['confirmation_code'])
        return Response(token, status=status.HTTP_200_OK)
