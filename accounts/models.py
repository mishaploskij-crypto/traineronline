from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    class Role(models.TextChoices):
        TRAINER = 'TR', _('Тренер')
        TRAINEE = 'TE', _('Тренирующийся')
        ADMIN = 'AD', _('Администратор')

    role = models.CharField(
        max_length=2,
        choices=Role.choices,
        default=Role.TRAINEE,
        verbose_name=_('Роль')
    )
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Телефон'))
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name=_('Аватар'))
    bio = models.TextField(blank=True, verbose_name=_('О себе'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))

    # Поля для тренера
    specialization = models.CharField(max_length=200, blank=True, verbose_name=_('Специализация'))
    experience_years = models.IntegerField(default=0, verbose_name=_('Опыт (лет)'))
    education = models.TextField(blank=True, verbose_name=_('Образование'))

    # Поля для тренирующегося
    birth_date = models.DateField(null=True, blank=True, verbose_name=_('Дата рождения'))
    fitness_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Новичок'),
            ('intermediate', 'Средний'),
            ('advanced', 'Продвинутый'),
        ],
        default='beginner',
        blank=True,
        verbose_name=_('Уровень подготовки')
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_trainer(self):
        return self.role == self.Role.TRAINER

    @property
    def is_trainee(self):
        return self.role == self.Role.TRAINEE

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def average_rating(self):
        if self.is_trainer:
            from ratings.models import TrainerRating
            ratings = TrainerRating.objects.filter(trainer=self)
            if ratings.exists():
                return ratings.aggregate(models.Avg('rating'))['rating__avg']
        return None

    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        ordering = ['-date_joined']