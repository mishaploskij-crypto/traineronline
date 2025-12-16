from django import forms
from django.utils.translation import gettext_lazy as _
from .models import TrainerRating


class RatingForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, '⭐️⭐️⭐️⭐️⭐️ - Отлично'),
        (4, '⭐️⭐️⭐️⭐️ - Хорошо'),
        (3, '⭐️⭐️⭐️ - Удовлетворительно'),
        (2, '⭐️⭐️ - Плохо'),
        (1, '⭐️ - Очень плохо'),
    ]

    rating = forms.ChoiceField(
        choices=RATING_CHOICES,
        widget=forms.RadioSelect,
        label=_('Ваша оценка')
    )

    class Meta:
        model = TrainerRating
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Оставьте ваш отзыв о тренере...'
            }),
        }

    def __init__(self, *args, **kwargs):
        self.trainer = kwargs.pop('trainer', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        rating = super().save(commit=False)
        if self.trainer:
            rating.trainer = self.trainer
        if self.user:
            rating.user = self.user
        if commit:
            rating.save()
        return rating