from django import forms

from posts.models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Сообщение',
            'group': 'Группа',
            'image': 'Изображение'
        }
        help_texts = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относится пост',
            'image': 'Выберите изображение'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Добавить комментарий'}
        help_texts = {'text': 'Текст комментария'}
