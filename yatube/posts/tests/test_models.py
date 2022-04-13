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

    def test_str_post_and_group(self):
        post = PostModelTest.post
        field_labels = {
            'text': 'Текст поста',
            'group': 'Группа',
        }
        for field, value in field_labels.items():
            with self.subTest(field=field):
                self.assertEqual(post._meta.get_field(field).verbose_name,
                                 value)
