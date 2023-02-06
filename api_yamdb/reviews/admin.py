from django.contrib import admin

from .models import Category, Genre, Title, Review, Comment, TitleGenre


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    empty_value_display = '-пусто-'


class TitleGenreInline(admin.TabularInline):
    model = TitleGenre
    extra = 1


class GenreAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'slug')
    empty_value_display = '-пусто-'
    inlines = [
        TitleGenreInline,
    ]


class TitleAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'year',
                    'category', 'description', 'genre_list')
    inlines = [
        TitleGenreInline,
    ]

    def genre_list(self, obj):
        return ', '.join([obj.name for obj in obj.genre.all()])
    genre_list.short_description = 'Жанры'


admin.site.register(Title, TitleAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Review)
admin.site.register(Comment)
