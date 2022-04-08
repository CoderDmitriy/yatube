from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='Truwermean',
                                            email='sciense01@hotmail.com',
                                            password='16London',),
            text='Тестовая запись для создания нового поста'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',)

    def test_str_post(self):
        post = PostModelTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_str_group(self):
        group = PostModelTest.group
        self.assertEqual(group.title, 'Тестовая группа')
