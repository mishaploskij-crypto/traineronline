from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Post, Category, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    def post_count(self, obj):
        return obj.posts.count()

    post_count.short_description = 'Количество постов'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'publish', 'views')
    list_filter = ('status', 'category', 'publish', 'author')
    search_fields = ('title', 'content', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', '-publish')

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'content', 'category', 'image', 'status')
        }),
        ('Мета-информация', {
            'fields': ('publish', 'views'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('author__username', 'post__title', 'content')
    actions = ['approve_comments']

    def approve_comments(self, request, queryset):
        queryset.update(active=True)

    approve_comments.short_description = "Одобрить выбранные комментарии"