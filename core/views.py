from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.views.generic import TemplateView
from posts.models import Post
from accounts.models import User


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Последние посты
        context['latest_posts'] = Post.objects.filter(
            status=Post.Status.PUBLISHED
        ).order_by('-publish')[:6]

        # Лучшие тренеры по рейтингу
        trainers = User.objects.filter(role=User.Role.TRAINER)
        trainers_with_rating = []
        for trainer in trainers:
            avg_rating = trainer.average_rating
            if avg_rating:
                trainers_with_rating.append((trainer, avg_rating))

        # Сортировка по рейтингу
        trainers_with_rating.sort(key=lambda x: x[1], reverse=True)
        context['top_trainers'] = trainers_with_rating[:5]

        return context


def about_view(request):
    return render(request, 'core/about.html')


def contact_view(request):
    return render(request, 'core/contact.html')