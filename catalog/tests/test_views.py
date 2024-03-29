import uuid

from datetime import date, timedelta

from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from catalog.models import Author, Book, BookInstance, Genre, Language


class TestViewsSetUp(TestCase):
    @classmethod
    def setUpTestData(cls):
        test_user1 = User.objects.create_user(username='testuser1', password='1X<ISRUkw+tuK')
        test_user2 = User.objects.create_user(username='testuser2', password='2HJ1vRV0Z&3iD')
        test_user1.save()
        test_user2.save()

        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)
        test_user2.save()

        number_of_authors = 13
        for author_id in range(number_of_authors):
            Author.objects.create(
                first_name=f'Christian {author_id}',
                last_name=f'Surname {author_id}'
            )

        test_author = Author.objects.get(pk=1)
        Genre.objects.create(name='Fantasy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(
            title='Book Title',
            summary='My book summary',
            isbn='1234567891123',
            author=test_author,
            language=test_language
        )
        number_of_books = 13
        for book_id in range(number_of_books):
            test_book_loop = Book.objects.create(
                title=f'Test Book {book_id}',
                author=test_author,
                summary=f'Test Summary {book_id}',
                isbn=book_id,
                language=test_language,
            )
            test_book_loop.genre.set(Genre.objects.all())
            test_book_loop.save()
        # This is for many to many relationships
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book)
        test_book.save()

        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + timedelta(days=book_copy % 5)
            the_borrower = test_user1 if book_copy % 2 else test_user2
            status = 'm'
            BookInstance.objects.create(
                book=test_book,
                imprint='Unlikely Imprint, 2016',
                due_back=return_date,
                borrower=the_borrower,
                status=status,
            )
        cls.author = test_author
        cls.language = test_language
        cls.genre_ids = ', '.join(map(str,[genre.pk for genre in genre_objects_for_book]))
        cls.test_book = test_book
        cls.test_book_instance = BookInstance.objects.all()[0]


class BookListViewTest(TestViewsSetUp):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/books/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('books'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertTrue(len(response.context['book_list']) == 10)

    def test_lists_all_books(self):
        response = self.client.get(reverse('books') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertTrue(len(response.context['book_list']) == 4)


class BookDetailViewTest(TestViewsSetUp):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/book/1')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        book = Book.objects.get(pk=1)
        response = self.client.get(reverse('book-detail', kwargs={'pk': book.pk}))
        self.assertEqual(response.status_code, 200)


class BookCreateViewTest(TestViewsSetUp):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('book-create'))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)  # 302 == redirect
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('book-create'))
        self.assertEqual(response.status_code, 403)  # 403 == forbidden

    def test_logged_in_with_permission_create_author(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-create'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_form.html')

    def test_form_submission(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        post = {'title': 'Test Book', 'summary': 'Test Summary',
                'isbn': '1234567890123', 'author': self.author.pk,
                'language': self.language.pk, 'genre': self.genre_ids}
        response = self.client.post(reverse('book-create'), post)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('book-detail',
                                               kwargs={'pk': Book.objects.get(pk=15).pk}))


class BookUpdateViewTest(TestViewsSetUp):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)  # 302 == redirect
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 403)  # 403 == forbidden

    def test_logged_in_with_permission_create_author(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-update', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_form.html')

    def test_form_submission(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        post = {'title': 'test2', 'author': self.author.pk, 'summary': 'update test',
                'isbn': '123', 'genre': self.genre_ids, 'language': self.language.pk}
        response = self.client.post(reverse('book-update', kwargs={'pk': self.test_book.pk, }), post)
        self.assertRedirects(response, reverse('book-detail', kwargs={'pk': self.test_book.pk}))
        self.assertEqual(response.status_code, 302)


class BookDeleteViewTest(TestViewsSetUp):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('book-delete', kwargs={'pk': self.test_book.pk + 1}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)  # 302 == redirect
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('book-delete', kwargs={'pk': self.test_book.pk + 1}))
        self.assertEqual(response.status_code, 403)  # 403 == forbidden

    def test_logged_in_with_permission(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-delete', kwargs={'pk': self.test_book.pk + 1}))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('book-delete', kwargs={'pk': self.test_book.pk + 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_delete.html')

    def test_form_submission(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('book-delete', kwargs={'pk': self.test_book.pk + 1}))
        self.assertRedirects(response, reverse('books'))
        self.assertEqual(response.status_code, 302)


class AuthorListViewTest(TestViewsSetUp):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/authors/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)

    def test_pagination_is_ten(self):
        response = self.client.get(reverse('authors'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertTrue(len(response.context['author_list']) == 10)

    def test_lists_all_authors(self):
        response = self.client.get(reverse('authors') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertTrue(len(response.context['author_list']) == 3)


class AuthorDetailViewTest(TestViewsSetUp):

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/catalog/author/1')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('author-detail', kwargs={'pk': self.author.pk}))
        self.assertEqual(response.status_code, 200)


class AuthorCreateViewTest(TestViewsSetUp):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author_create'))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)  # 302 == redirect
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 403)  # 403 == forbidden

    def test_logged_in_with_permission_create_author(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_form_submission(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        post = {'first_name': 'Test', 'last_name': 'Case', 'date_of_birth': date.today(), }
        response = self.client.post(reverse('author_create'), post)
        authors = len(Author.objects.all())
        self.assertRedirects(response, reverse('author-detail', kwargs={'pk': authors}))
        self.assertEqual(response.status_code, 302)


class AuthorUpdateViewTest(TestViewsSetUp):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author_update', kwargs={'pk': self.author.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)  # 302 == redirect
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author_update', kwargs={'pk': self.author.pk}))
        self.assertEqual(response.status_code, 403)  # 403 == forbidden

    def test_logged_in_with_permission_create_author(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_update', kwargs={'pk': self.author.pk}))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_update', kwargs={'pk': self.author.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_form.html')

    def test_form_submission(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        post = {'first_name': 'Testee', 'last_name': 'Caseee', 'date_of_birth': date.today(), }
        response = self.client.post(reverse('author_update', kwargs={'pk': self.author.pk}), post)
        self.assertRedirects(response, reverse('author-detail', kwargs={'pk': self.author.pk}))
        self.assertEqual(response.status_code, 302)


class AuthorDeleteViewTest(TestViewsSetUp):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('author_delete', kwargs={'pk': 13}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)  # 302 == redirect
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('author_delete', kwargs={'pk': 13}))
        self.assertEqual(response.status_code, 403)  # 403 == forbidden

    def test_logged_in_with_permission_create_author(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_delete', kwargs={'pk': 13}))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('author_delete', kwargs={'pk': 13}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/author_delete.html')

    def test_form_submission(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.post(reverse('author_delete', kwargs={'pk': 13}))
        self.assertRedirects(response, reverse('authors'))
        self.assertEqual(response.status_code, 302)


class LoanedBookInstancesByUserListViewTest(TestViewsSetUp):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('my-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/mybooks/')

    def test_logged_in_uses_correct_template(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))

        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(response, 'catalog/bookinstance_list_borrowed_user.html')

    def test_only_borrowed_books_in_list(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        self.assertTrue('bookinstance_list' in response.context)
        self.assertEqual(len(response.context['bookinstance_list']), 0)

        # change books to be on loan, page is paginated so only need first 10
        books = BookInstance.objects.all()[:10]
        for book in books:
            book.status = 'o'
            book.save()

        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('bookinstance_list' in response.context)
        for bookitem in response.context['bookinstance_list']:
            self.assertEqual(response.context['user'], bookitem.borrower)
            self.assertEqual('o', bookitem.status)

    def test_pages_ordered_by_due_date(self):
        # Change all books to be on loan
        for book in BookInstance.objects.all():
            book.status = 'o'
            book.save()
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('my-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser1')
        self.assertEqual(response.status_code, 200)

        # Confirm pagination
        self.assertEqual(len(response.context['bookinstance_list']), 10)
        last_date = 0
        for book in response.context['bookinstance_list']:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


class AllLoanedBooksListView(TestViewsSetUp):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('all-borrowed'))
        self.assertRedirects(response, '/accounts/login/?next=/catalog/allloanedbooks/')

    def test_logged_in_uses_correct_template(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('all-borrowed'))
        self.assertEqual(str(response.context['user']), 'testuser2')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/all_loaned_books_list_view.html')

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('all-borrowed'))
        self.assertEqual(response.status_code, 403)  # 403 == forbidden

    def test_logged_has_all_content(self):
        book_instance_list = BookInstance.objects.all()
        for book_instance in book_instance_list:
            book_instance.status='o'
            book_instance.save()
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('all-borrowed'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        # 30 BookInstance total, 20 on page 1, 10 on page 2
        self.assertEqual(len(response.context['object_list']), 20)
        self.assertEqual(len(response.context['page_obj'].paginator.object_list), 30)
        self.assertEqual(response.context['page_obj'].paginator.num_pages, 2)


class RenewBookInstancesViewTest(TestViewsSetUp):

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_book_instance.pk}))
        # Manually check redirect (Can't use assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(response.status_code, 302)  # 302 == redirect
        self.assertTrue(response.url.startswith('/accounts/login/'))

    def test_redirect_if_logged_in_but_not_correct_permission(self):
        self.client.login(username='testuser1', password='1X<ISRUkw+tuK')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_book_instance.pk}))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_with_permission_borrowed_book(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_book_instance.pk}))
        self.assertEqual(response.status_code, 200)

    def test_logged_in_with_permission_another_users_borrowed_book(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_book_instance.pk}))
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid = uuid.uuid4()
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': test_uid}))
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_book_instance.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_3_weeks(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        response = self.client.get(reverse('renew-book-librarian', kwargs={'pk': self.test_book_instance.pk}))
        self.assertEqual(response.status_code, 200)
        date_3_weeks = date.today() + timedelta(weeks=3)
        self.assertEqual(response.context['form'].initial['due_back'], date_3_weeks)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        valid_date_in_future = date.today() + timedelta(weeks=2)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_book_instance.pk, })
                                    , {'due_back': valid_date_in_future})
        self.assertRedirects(response, reverse('all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        invalid_date_in_past = date.today() - timedelta(weeks=1)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_book_instance.pk, })
                                    , {'due_back': invalid_date_in_past})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_back', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_too_far_in_future(self):
        self.client.login(username='testuser2', password='2HJ1vRV0Z&3iD')
        invalid_date_in_future = date.today() + timedelta(weeks=5)
        response = self.client.post(reverse('renew-book-librarian', kwargs={'pk': self.test_book_instance.pk, })
                                    , {'due_back': invalid_date_in_future})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'due_back', 'Invalid date - renewal more than 4 weeks ahead')
