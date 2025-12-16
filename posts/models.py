from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from accounts.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Название'))
    slug = models.SlugField(unique=True, verbose_name=_('URL'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')
        ordering = ['name']


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', _('Черновик')
        PUBLISHED = 'PB', _('Опубликовано')

    title = models.CharField(max_length=200, verbose_name=_('Заголовок'))
    slug = models.SlugField(max_length=200, unique_for_date='publish', verbose_name=_('URL'))
    content = models.TextField(verbose_name=_('Содержание'))
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        limit_choices_to={'role': User.Role.TRAINER},
        verbose_name=_('Автор')
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts',
        verbose_name=_('Категория')
    )
    publish = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата публикации'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    status = models.CharField(
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name=_('Статус')
    )
    image = models.ImageField(upload_to='posts/%Y/%m/%d/', blank=True, verbose_name=_('Изображение'))
    views = models.PositiveIntegerField(default=0, verbose_name=_('Просмотры'))

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('posts:post_detail', args=[self.slug])

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    class Meta:
        verbose_name = _('Пост')
        verbose_name_plural = _('Посты')
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish']),
        ]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Пост'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Автор'))
    content = models.TextField(verbose_name=_('Комментарий'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))
    active = models.BooleanField(default=True, verbose_name=_('Активен'))

    class Meta:
        ordering = ['created']
        indexes = [
            models.Index(fields=['created']),
        ]

    def __str__(self):
        return f'Комментарий от {self.author} к посту "{self.post.title}"'