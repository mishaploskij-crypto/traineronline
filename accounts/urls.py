from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
    UserProfileView, UserUpdateView, TrainerListView,
    dashboard_view, trainer_dashboard, trainee_dashboard
)

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профили
    path('profile/<int:pk>/', UserProfileView.as_view(), name='profile'),
    path('profile/update/', UserUpdateView.as_view(), name='profile_update'),

    # Дашборды
    path('dashboard/', dashboard_view, name='dashboard'),
    path('dashboard/trainer/', trainer_dashboard, name='trainer_dashboard'),
    path('dashboard/trainee/', trainee_dashboard, name='trainee_dashboard'),

    # Список тренеров
    path('trainers/', TrainerListView.as_view(), name='trainer_list'),
    path('trainer/<int:pk>/', UserProfileView.as_view(), name='trainer_profile'),

    # Восстановление пароля
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html'
         ),
         name='password_reset'),
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html'
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]