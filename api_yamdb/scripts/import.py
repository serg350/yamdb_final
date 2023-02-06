from reviews.models import Review, Genre, Category, Title, Comment
import csv

from users.models import User


def genre_import():
    with open('static/data/genre.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        Genre.objects.all().delete()
        for row in reader:
            print(row)
            genre = Genre.objects.create(id=row[0],
                                         name=row[1],
                                         slug=row[2])
            genre.save()


def category_import():
    with open('static/data/category.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        Category.objects.all().delete()
        for row in reader:
            print(row)
            category = Category.objects.create(id=row[0],
                                               name=row[1],
                                               slug=row[2])
            category.save()


def title_import():
    with open('static/data/titles.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        Title.objects.all().delete()
        for row in reader:
            print(row)
            category = Category.objects.get(id=row[3])
            title = Title.objects.create(id=row[0],
                                         name=row[1],
                                         year=row[2],
                                         category=category,
                                         )
            title.save()


def title_genre_import():
    with open('static/data/genre_title.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        for row in reader:
            print(row)
            genre = Genre.objects.get(pk=row[2])
            title = Title.objects.get(pk=row[1])
            title.genre.add(genre)
            title.save()


def review_import():
    with open('static/data/review.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        Review.objects.all().delete()
        for row in reader:
            print(row)
            author = User.objects.get(id=row[3])
            review = Review.objects.create(id=row[0],
                                           title_id=row[1],
                                           text=row[2],
                                           author=author,
                                           score=row[4],
                                           pub_date=row[5]
                                           )
            review.save()


def user_import():
    with open('static/data/users.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        User.objects.all().delete()
        for row in reader:
            print(row)
            user = User.objects.create(id=row[0],
                                       username=row[1],
                                       email=row[2],
                                       role=row[3],
                                       bio=row[4],
                                       first_name=row[5],
                                       last_name=row[5]
                                       )
            user.save()


def comments_import():
    with open('static/data/comments.csv', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # Advance past the header
        Comment.objects.all().delete()
        for row in reader:
            print(row)
            author = User.objects.get(id=row[3])
            comment = Comment.objects.create(id=row[0],
                                             review_id=row[1],
                                             text=row[2],
                                             author=author,
                                             pub_date=row[4],
                                             )
            comment.save()


def run():
    user_import()
    genre_import()
    category_import()
    title_import()
    title_genre_import()
    review_import()
    comments_import()
