from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import TrainerRating, TrainerStatistic


@admin.register(TrainerRating)
class TrainerRatingAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'user', 'rating', 'created_at', 'updated_at')
    list_filter = ('rating', 'created_at', 'trainer')
    search_fields = ('trainer__username', 'user__username', 'comment')
    raw_id_fields = ('trainer', 'user')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


@admin.register(TrainerStatistic)
class TrainerStatisticAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'total_ratings', 'average_rating', 'last_updated')
    list_filter = ('last_updated',)
    search_fields = ('trainer__username',)
    readonly_fields = ('total_ratings', 'average_rating', 'five_star_count',
                      'four_star_count', 'three_star_count', 'two_star_count',
                      'one_star_count', 'last_updated')