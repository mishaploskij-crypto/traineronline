from django.urls import path
from . import views

urlpatterns = [
    path('trainer/<int:trainer_id>/rate/', views.rate_trainer, name='rate_trainer'),
    path('rating/<int:rating_id>/update/', views.update_rating, name='update_rating'),
    path('rating/<int:rating_id>/delete/', views.delete_rating, name='delete_rating'),
    path('trainer/<int:trainer_id>/all/', views.trainer_ratings, name='trainer_ratings'),
]