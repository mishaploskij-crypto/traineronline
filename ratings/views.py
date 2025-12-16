from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.db.models import Avg, Count, Q
from .models import TrainerRating, TrainerStatistic
from .forms import RatingForm
from accounts.models import User


@login_required
def rate_trainer(request, trainer_id):
    trainer = get_object_or_404(User, pk=trainer_id, role=User.Role.TRAINER)

    # Проверяем, не оценивал ли уже пользователь этого тренера
    existing_rating = TrainerRating.objects.filter(
        trainer=trainer,
        user=request.user
    ).first()

    if existing_rating:
        messages.info(request, 'Вы уже оценили этого тренера.')
        return redirect('trainer_profile', pk=trainer_id)

    if request.method == 'POST':
        form = RatingForm(request.POST, trainer=trainer, user=request.user)
        if form.is_valid():
            rating = form.save()

            # Обновляем статистику тренера
            statistic, created = TrainerStatistic.objects.get_or_create(trainer=trainer)
            statistic.update_statistics()

            messages.success(request, 'Спасибо за вашу оценку!')
            return redirect('trainer_profile', pk=trainer_id)
    else:
        form = RatingForm(trainer=trainer, user=request.user)

    context = {
        'form': form,
        'trainer': trainer,
    }
    return render(request, 'ratings/rate_trainer.html', context)


@login_required
def update_rating(request, rating_id):
    rating = get_object_or_404(TrainerRating, pk=rating_id, user=request.user)
    trainer = rating.trainer

    if request.method == 'POST':
        form = RatingForm(request.POST, instance=rating, trainer=trainer, user=request.user)
        if form.is_valid():
            form.save()

            # Обновляем статистику тренера
            statistic, created = TrainerStatistic.objects.get_or_create(trainer=trainer)
            statistic.update_statistics()

            messages.success(request, 'Ваша оценка обновлена!')
            return redirect('trainer_profile', pk=trainer.pk)
    else:
        form = RatingForm(instance=rating, trainer=trainer, user=request.user)

    context = {
        'form': form,
        'trainer': trainer,
        'rating': rating,
    }
    return render(request, 'ratings/update_rating.html', context)


@login_required
def delete_rating(request, rating_id):
    rating = get_object_or_404(TrainerRating, pk=rating_id, user=request.user)
    trainer_id = rating.trainer.pk

    rating.delete()

    # Обновляем статистику тренера
    statistic, created = TrainerStatistic.objects.get_or_create(trainer=rating.trainer)
    statistic.update_statistics()

    messages.success(request, 'Ваша оценка удалена!')
    return redirect('trainer_profile', pk=trainer_id)


def trainer_ratings(request, trainer_id):
    trainer = get_object_or_404(User, pk=trainer_id, role=User.Role.TRAINER)
    ratings = TrainerRating.objects.filter(trainer=trainer).order_by('-created_at')

    # Статистика
    statistics = {
        'total': ratings.count(),
        'average': ratings.aggregate(Avg('rating'))['rating__avg'] or 0,
        'distribution': {
            5: ratings.filter(rating=5).count(),
            4: ratings.filter(rating=4).count(),
            3: ratings.filter(rating=3).count(),
            2: ratings.filter(rating=2).count(),
            1: ratings.filter(rating=1).count(),
        }
    }

    context = {
        'trainer': trainer,
        'ratings': ratings,
        'statistics': statistics,
    }
    return render(request, 'ratings/trainer_ratings.html', context)