from django.db import models

# Create your models here.
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


class TrainerRating(models.Model):
    trainer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings_received',
        limit_choices_to={'role': User.Role.TRAINER},
        verbose_name=_('Тренер')
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='ratings_given',
        verbose_name=_('Пользователь')
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name=_('Оценка')
    )
    comment = models.TextField(blank=True, verbose_name=_('Комментарий'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Оценка тренера')
        verbose_name_plural = _('Оценки тренеров')
        unique_together = ['trainer', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.rating} звезд для {self.trainer} от {self.user}'


class TrainerStatistic(models.Model):
    trainer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='statistics',
        limit_choices_to={'role': User.Role.TRAINER},
        verbose_name=_('Тренер')
    )
    total_ratings = models.IntegerField(default=0, verbose_name=_('Всего оценок'))
    average_rating = models.FloatField(default=0.0, verbose_name=_('Средний рейтинг'))
    five_star_count = models.IntegerField(default=0, verbose_name=_('5 звезд'))
    four_star_count = models.IntegerField(default=0, verbose_name=_('4 звезды'))
    three_star_count = models.IntegerField(default=0, verbose_name=_('3 звезды'))
    two_star_count = models.IntegerField(default=0, verbose_name=_('2 звезды'))
    one_star_count = models.IntegerField(default=0, verbose_name=_('1 звезда'))
    last_updated = models.DateTimeField(auto_now=True, verbose_name=_('Последнее обновление'))

    def update_statistics(self):
        ratings = self.trainer.ratings_received.all()
        self.total_ratings = ratings.count()

        if self.total_ratings > 0:
            self.average_rating = ratings.aggregate(models.Avg('rating'))['rating__avg']
            self.five_star_count = ratings.filter(rating=5).count()
            self.four_star_count = ratings.filter(rating=4).count()
            self.three_star_count = ratings.filter(rating=3).count()
            self.two_star_count = ratings.filter(rating=2).count()
            self.one_star_count = ratings.filter(rating=1).count()

        self.save()

    def __str__(self):
        return f'Статистика для {self.trainer}'

    class Meta:
        verbose_name = _('Статистика тренера')
        verbose_name_plural = _('Статистика тренеров')