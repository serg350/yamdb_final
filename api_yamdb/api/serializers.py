from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.validators import UniqueTogetherValidator

from api_yamdb.settings import (AUTH_USERNAME_MAXLENGTH,
                                AUTH_EMAIL_MAXLENGTH,
                                AUTH_CONF_CODE_MAXLENGTH)
from .validators import validate_username, validate_year
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class CategoriesSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Category
        extra_kwargs = {'slug': {'required': True}}


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('name', 'slug')
        model = Genre
        extra_kwargs = {'slug': {'required': True}}


class TitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    rating = serializers.IntegerField(read_only=True)
    year = serializers.IntegerField(validators=[validate_year])

    class Meta:
        fields = '__all__'
        model = Title

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['genre'] = GenreSerializer(instance.genre, many=True).data
        response['category'] = CategoriesSerializer(instance.category).data
        return response


class TitleDefault:
    requires_context = True

    def __call__(self, data):
        return get_object_or_404(
            Title,
            id=data.context['view'].kwargs.get('title_id')
        )


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    title = serializers.HiddenField(default=TitleDefault())
    score = serializers.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        fields = '__all__'
        model = Review
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['author', 'title']
            )
        ]


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('review', )


class ValidateUsernameMixin:
    def validate_username(self, value):
        return validate_username(value)


class AuthSerializer(serializers.Serializer, ValidateUsernameMixin):
    username = serializers.CharField(
        max_length=AUTH_USERNAME_MAXLENGTH,
        required=True
    )


class RegisterSerializer(AuthSerializer):
    email = serializers.EmailField(
        max_length=AUTH_EMAIL_MAXLENGTH,
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'email')


class GetTokenSerializer(AuthSerializer):
    confirmation_code = serializers.CharField(
        max_length=AUTH_CONF_CODE_MAXLENGTH,
        required=True
    )

    def validate(self, data):
        try:
            username = data.get('username')
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise NotFound(
                detail=f'Пользователя с именем {username} не существует.'
            )
        if user.confirmation_code != data.get('confirmation_code'):
            raise serializers.ValidationError(
                'Некорректный код подтверждения.')
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')
