from datetime import date, timedelta

from django.test import TestCase
from django.utils import timezone

from catalog.forms import RenewBookForm


class RenewBookFormTest(TestCase):
    def test_renew_form_labels(self):
        form = RenewBookForm()
        self.assertTrue(form.fields['renewal_date'].label is None or
                        form.fields['renewal_date'].label == 'renewal date')
        self.assertEqual(form.fields['renewal_date'].help_text,
                         "Enter a date between now and 4 weeks (default 3).")

    def test_renew_form_date_in_past(self):
        testDate = date.today() - timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': testDate})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_too_far_in_future(self):
        testDate = date.today() + timedelta(weeks=4) + timedelta(days=1)
        form = RenewBookForm(data={'renewal_date': testDate})
        self.assertFalse(form.is_valid())

    def test_renew_form_date_today(self):
        testDate = date.today()
        form = RenewBookForm(data={'renewal_date': testDate})
        self.assertTrue(form.is_valid())

    def test_renew_form_date_max(self):
        testDate = timezone.localtime() + timedelta(weeks=4)
        form = RenewBookForm(data={'renewal_date': testDate})
        self.assertTrue(form.is_valid())
