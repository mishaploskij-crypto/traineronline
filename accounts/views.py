from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import DetailView, UpdateView, ListView
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q, Avg, Count
from .models import User
from .forms import UserRegisterForm, UserUpdateForm, TrainerProfileForm, TraineeProfileForm
from ratings.models import TrainerRating


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Вы успешно вошли в систему.')

            # Перенаправление в зависимости от роли
            if user.is_trainer:
                return redirect('trainer_dashboard')
            elif user.is_trainee:
                return redirect('trainee_dashboard')
            else:
                return redirect('admin:index')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')
    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('home')


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    template_name = 'accounts/profile.html'
    context_object_name = 'profile_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object

        if user.is_trainer:
            # Получаем рейтинги тренера
            context['ratings'] = TrainerRating.objects.filter(
                trainer=user
            ).order_by('-created_at')[:10]

            # Получаем статистику
            context['statistics'] = {
                'total_ratings': user.ratings_received.count(),
                'average_rating': user.average_rating,
            }

            # Последние посты тренера
            context['posts'] = user.posts.filter(
                status='PB'
            ).order_by('-publish')[:5]

        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'accounts/profile_update.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        messages.success(self.request, 'Ваш профиль успешно обновлен!')
        return reverse_lazy('profile', kwargs={'pk': self.request.user.pk})


class TrainerListView(ListView):
    model = User
    template_name = 'accounts/trainer_list.html'
    context_object_name = 'trainers'
    paginate_by = 12

    def get_queryset(self):
        queryset = User.objects.filter(role=User.Role.TRAINER).order_by('-date_joined')

        # Фильтрация по специализации
        specialization = self.request.GET.get('specialization')
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)

        # Фильтрация по опыту
        experience = self.request.GET.get('experience')
        if experience:
            queryset = queryset.filter(experience_years__gte=int(experience))

        # Сортировка
        sort = self.request.GET.get('sort', 'newest')
        if sort == 'rating':
            # Сложная сортировка по рейтингу
            trainers_with_rating = []
            for trainer in queryset:
                avg_rating = trainer.average_rating or 0
                trainers_with_rating.append((trainer, avg_rating))

            trainers_with_rating.sort(key=lambda x: x[1], reverse=True)
            return [trainer for trainer, _ in trainers_with_rating]
        elif sort == 'experience':
            queryset = queryset.order_by('-experience_years')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specializations'] = User.objects.filter(
            role=User.Role.TRAINER
        ).values_list('specialization', flat=True).distinct()
        return context


@login_required
def dashboard_view(request):
    if request.user.is_trainer:
        return trainer_dashboard(request)
    elif request.user.is_trainee:
        return trainee_dashboard(request)
    else:
        return redirect('admin:index')


@login_required
def trainer_dashboard(request):
    user = request.user
    posts = user.posts.all().order_by('-publish')[:5]
    ratings = user.ratings_received.all().order_by('-created_at')[:5]

    context = {
        'posts': posts,
        'ratings': ratings,
        'total_posts': user.posts.count(),
        'total_ratings': user.ratings_received.count(),
        'average_rating': user.average_rating,
    }
    return render(request, 'accounts/trainer_dashboard.html', context)


@login_required
def trainee_dashboard(request):
    user = request.user
    ratings_given = user.ratings_given.all().order_by('-created_at')[:5]

    context = {
        'ratings_given': ratings_given,
        'total_ratings_given': user.ratings_given.count(),
    }
    return render(request, 'accounts/trainee_dashboard.html', context)