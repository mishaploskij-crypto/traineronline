from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    ROLE_CHOICES = [
        (User.Role.TRAINEE, 'Тренирующийся'),
        (User.Role.TRAINER, 'Тренер'),
    ]

    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial=User.Role.TRAINEE,
        label='Тип аккаунта'
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone', 'first_name', 'last_name',
            'role', 'password1', 'password2'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[
            'username'].help_text = 'Обязательное поле. 150 символов или меньше. Только буквы, цифры и @/./+/-/_'
        self.fields['email'].help_text = 'Обязательное поле. Введите действительный адрес электронной почты.'

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        if commit:
            user.save()
        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'avatar',
            'bio', 'specialization', 'experience_years', 'education',
            'birth_date', 'fitness_level'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
            'education': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Скрываем поля, не относящиеся к роли пользователя
        if not self.instance.is_trainer:
            self.fields.pop('specialization', None)
            self.fields.pop('experience_years', None)
            self.fields.pop('education', None)
        if not self.instance.is_trainee:
            self.fields.pop('birth_date', None)
            self.fields.pop('fitness_level', None)


class TrainerProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'specialization', 'experience_years', 'education',
            'bio', 'avatar'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'education': forms.Textarea(attrs={'rows': 4}),
        }


class TraineeProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['birth_date', 'fitness_level', 'bio', 'avatar']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }