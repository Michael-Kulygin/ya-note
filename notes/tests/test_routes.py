from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='user')
        cls.reader = User.objects.create(username='reader')
        cls.note = Note.objects.create(
            title='title', text='title', author=cls.author, slug='slug'
        )

    def test_home_availability_for_anonymous_user(self):
        home_page_url = reverse('notes:home')
        response = self.client.get(home_page_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        self.client.force_login(self.author)

        urls = (
            ('notes:home', None),
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('users:login', None),
            ('users:signup', None),
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_user(self):
        self.client.force_login(self.reader)
        for name  in ('notes:edit', 'notes:delete', 'notes:detail'):
            with self.subTest(name=name):
                url = reverse(name, args=(self.note.slug,))
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_availability_for_comment_edit_and_delete(self):
        user_statuses = (
            (self.author, HTTPStatus.OK),
        )
        for user, status in user_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_user(self):
        login_url = reverse('users:login')

        urls = (
            ('notes:list', None),
            ('notes:success', None),
            ('notes:add', None),
            ('notes:detail', (self.note.slug,)),
            ('notes:edit', (self.note.slug,)),
            ('notes:delete', (self.note.slug,))
        )

        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)


    def test_logout_availability_for_all_users(self):
        url = reverse('users:logout')

        users = (
            ('author', self.author),
            ('reader', self.reader),
        )

        for user_type, user in users:
            with self.subTest(user=user_type):
                if user is None:
                    self.client.logout()
                else:
                    self.client.force_login(user)
                response = self.client.post(url)  # POST, не GET
                self.assertEqual(response.status_code, HTTPStatus.OK)
