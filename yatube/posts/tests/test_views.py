import shutil
import tempfile

from http.client import OK

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, Follow, Comment
from posts.utils import POST_COUNT

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post_1 = Post.objects.create(
            author=User.objects.create_user(username='Truwermean1',
                                            email='twentydays@hotmail.com',
                                            password='15London',),
            text='Тестовая запись для создания 1 поста',
            group=Group.objects.create(
                title='Заголовок для 1 тестовой группы',
                slug='test-slug1'))

        cls.post_2 = Post.objects.create(
            author=User.objects.create_user(username='Truwermean2',
                                            email='twentydays2@hotmail.com',
                                            password='15London',),
            text='Тестовая запись для создания 2 поста',
            group=Group.objects.create(
                title='Заголовок для 2 тестовой группы',
                slug='test-slug2'),
            image=uploaded)
        cls.comments = Comment.objects.create(
            author=User.objects.create_user(username='Truwermean',
                                            email='twentydays1@hotmail.com',
                                            password='15London',),
            post=cls.post_2,
            text='Текст комментария'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='Nolan')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post(self, first_object, post):
        group_title_0 = first_object.group.title
        group_slug_0 = first_object.group.slug
        post_pk = first_object.id
        post_text = first_object.text
        post_image = Post.objects.first().image
        self.assertEqual(post_image, 'posts/small.gif')
        self.assertEqual(post_pk, post.id)
        self.assertEqual(post_text, post.text)
        self.assertEqual(group_title_0, post.group.title)
        self.assertEqual(group_slug_0, post.group.slug)

    def test_pages_used_correct_template(self):
        """ Проверяем чтобы урлы использовали соответствующий шаблон. """
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug':
                                                    PostTests.post_2.
                                                    group.slug})
            ),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """ Шаблон индекс сделан с правильным контекстом. """
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(response.status_code, OK)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.author.username,
                         self.post_2.author.username)
        self.check_post(first_object, self.post_2)

    def test_group_pages_show_correct_context(self):
        """ Шаблон группы и поста """
        response = self.authorized_client.get(reverse
                                              ('posts:group_list',
                                               kwargs={'slug':
                                                       PostTests.post_2.
                                                       group.slug}))
        for post_example in response.context.get('page_obj').object_list:
            with self.subTest():
                self.assertIsInstance(post_example, Post)
                self.assertEqual(post_example.group.id, self.post_2.group.id)
        first_object = response.context['page_obj'][0]
        self.check_post(first_object, self.post_2)

    def test_post_another_group(self):
        """ Пост не попал в другую группу """
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={
                'slug': PostTests.post_1.group.slug}))
        first_object = response.context.get('page_obj').object_list
        self.assertNotIn(self.post_1.id, first_object)

    def test_post_create_show_correct_context(self):
        """ Шаблон сделан с правильным контекстом. """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_profile_correct_context(self):
        """ Шаблон профайла сделан с правильным контекстом """
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username':
                                             self.post_2.author.username}))
        first_object = response.context['page_obj'][0]
        self.check_post(first_object, self.post_2)

    def test_post_detail(self):
        """ Проверка картинки на отдельную страницу поста """
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post_2.pk}))
        first_object = response.context.get('post')
        self.assertIsNotNone(first_object)
        self.check_post(first_object, self.post_2)
        comment = response.context.get('comments')[0]
        self.assertEqual(comment.text, self.comments.text)
        self.assertEqual(comment.post, self.comments.post)
        self.assertEqual(
            comment.author.username, self.comments.author.username)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Truwermean',
                                              email='sciense01@hotmail.com',
                                              password='16London',)
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='test-slug2',
            description='Тестовое описание')
        cls.posts = []
        for i in range(13):
            cls.posts.append(Post(
                text=f'Тестовый пост {i}',
                author=cls.author,
                group=cls.group
            )
            )
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.user = User.objects.create_user(username='Nolan')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_posts(self):
        list_urls = {
            reverse('posts:index'): 'posts/index',
            reverse('posts:group_list', kwargs={
                'slug': PaginatorViewsTest.group.slug}): 'group',
            reverse('posts:profile', kwargs={'username':
                                             self.author.username}):
            'profile',
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
        self.assertEqual(len(response.context.get('page_obj').object_list),
                         POST_COUNT)

    def test_second_page_contains_three_posts(self):
        list_urls = {
            reverse('posts:index') + '?page=2': 'posts/index',
            reverse('posts:group_list', kwargs={
                'slug': PaginatorViewsTest.group.slug})
            + '?page=2': 'group',
            reverse('posts:profile', kwargs={'username': self.author.username})
            + '?page=2':
            'profile',
        }
        for tested_url in list_urls.keys():
            response = self.client.get(tested_url)
        self.assertEqual(len(response.context.get('page_obj').object_list),
                         Post.objects.count() % POST_COUNT)


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='NolanStross',
                                            email='twentydays03@hotmail.com',
                                            password='15London',),
            text='Тестовая запись')

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username='Nolan')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache_index(self):
        """ Тест кэша страницы index """
        first_check = self.authorized_client.get(reverse('posts:index'))
        post_1 = Post.objects.get(pk=1)
        post_1.text = 'Измененный текст'
        post_1.save()
        second_check = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(first_check.content, second_check.content)
        cache.clear()
        third_check = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(first_check.content, third_check.content)


class FollowTests(TestCase):
    def setUp(self):
        self.client_auth_follower = Client()
        self.client_auth_following = Client()
        self.user_follower = User.objects.create_user(username='follower',
                                                      email='test_mail@bk.ru',
                                                      password='15London')
        self.user_following = User.objects.create_user(username='following',
                                                       email='test_mol1@bk.ru',
                                                       password='15London')
        self.post = Post.objects.create(
            author=self.user_following,
            text='Тестовая запись для тестирования ленты'
        )
        self.client_auth_follower.force_login(self.user_follower)
        self.client_auth_following.force_login(self.user_following)

    def test_follow(self):
        """ Проверка подписки """
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.assertEqual(Follow.objects.all().count(), 1)

    def test_unfollow(self):
        """ Проверка отписки """
        self.client_auth_follower.get(reverse('posts:profile_follow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.client_auth_follower.get(reverse('posts:profile_unfollow',
                                              kwargs={'username':
                                                      self.user_following.
                                                      username}))
        self.assertEqual(Follow.objects.all().count(), 0)

    def test_subscription_feed(self):
        """ Проверка чтобы запись появлялась в ленте подписчиков """
        Follow.objects.create(user=self.user_follower,
                              author=self.user_following)
        response = self.client_auth_follower.get('/follow/')
        post_text = response.context.get('page_obj')[0].text
        self.assertEqual(post_text, self.post.text)
        response = self.client_auth_following.get('/follow/')
        self.assertNotContains(response, self.post.text)

    def test_add_comment(self):
        """
        Проверка комментирования
        неавторизованным и
        авторизованным пользователям
        """
        comments_count = Comment.objects.count()
        id = self.post.id

        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.client.post(
            reverse('posts:add_comment', args=[id]))
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.id}/comment/')
        # Проверка авторизованным пользователям
        response = self.client_auth_follower.post(
            reverse('posts:add_comment', args=[id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', args=[id]))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(Comment.objects.all()[0].text, form_data['text'])
