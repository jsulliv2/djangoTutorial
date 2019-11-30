from django.test import TestCase

from catalog.models import *


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Genre.objects.create(name='Testing')

    def test_labels(self):
        genre = Genre.objects.get(id=1)
        name = genre._meta.get_field('name')
        self.assertEquals(name.verbose_name, 'name')
        self.assertEquals(name.max_length, 200)
        self.assertEquals(name.help_text, 'Enter a book genre (e.g. Science Fiction)')


class LanguageModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Language.objects.create(name='English')

    def test_labels(self):
        language = Language.objects.get(id=1)
        name = language._meta.get_field('name')
        self.assertEquals(name.verbose_name, 'name')
        self.assertEquals(name.max_length, 100)
        self.assertEquals(name.help_text, "Enter the book's natural language (e.g. English)")


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Author.objects.create(first_name='Big', last_name='Bob')

    def test_labels(self):
        author = Author.objects.get(id=1)
        first_name = author._meta.get_field('first_name').verbose_name
        self.assertEquals(first_name, 'first name')
        first_name_max_length = author._meta.get_field('first_name').max_length
        self.assertEquals(first_name_max_length, 100)
        last_name = author._meta.get_field('last_name').verbose_name
        self.assertEquals(last_name, 'last name')
        last_name_max_length = author._meta.get_field('last_name').max_length
        self.assertEquals(last_name_max_length, 100)
        date_of_birth = author._meta.get_field('date_of_birth').verbose_name
        self.assertEquals(date_of_birth, 'date of birth')
        date_of_death = author._meta.get_field('date_of_death').verbose_name
        self.assertEquals(date_of_death, 'Died')
        expected_object_name = f'{author.last_name}, {author.first_name}'
        self.assertEquals(expected_object_name, 'Bob, Big')

    def test_get_absolute_url(self):
        author = Author.objects.get(id=1)
        self.assertEquals(author.get_absolute_url(), '/catalog/author/1')


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.create(first_name='Big', last_name='Bob')
        Genre.objects.create(name='Testing')
        genre_book_objects = Genre.objects.all()
        language = Language.objects.create(name='English')
        testBook = Book.objects.create(title='Test Book',
                                       summary='This is my test book',
                                       isbn='1234567891123',
                                       author=author,
                                       language=language)
        testBook.genre.set(genre_book_objects)
        testBook.save()

    def test_labels(self):
        book = Book.objects.get(id=1)
        title = book._meta.get_field('title')
        self.assertEquals(title.verbose_name, 'title')
        self.assertEquals(title.max_length, 200)
        author = book._meta.get_field('author')
        self.assertEquals(author.verbose_name, 'author')
        self.assertEquals(author.null, True)
        summary = book._meta.get_field('summary')
        self.assertEquals(summary.verbose_name, 'summary')
        self.assertEquals(summary.max_length, 1000)
        self.assertEquals(summary.help_text, 'Enter a brief description of the book.')
        isbn = book._meta.get_field('isbn')
        self.assertEquals(isbn.verbose_name, 'ISBN')
        self.assertEquals(isbn.max_length, 13)
        self.assertEquals(isbn.help_text,
                          '13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
        genre = book._meta.get_field('genre')
        self.assertEquals(genre.verbose_name, 'genre')
        self.assertEquals(genre.help_text, 'Select a genre for this book')
        language = book._meta.get_field('language')
        self.assertEquals(language.verbose_name, 'language')
        self.assertEquals(language.null, True)

    def test_get_absolute_url(self):
        book = Book.objects.get(id=1)
        self.assertEquals(book.get_absolute_url(), '/catalog/book/1')

    def test_display_genre(self):
        book = Book.objects.get(id=1)
        self.assertEquals(book.display_genre(), 'Testing')
