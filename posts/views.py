from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
from accounts.models import User


class PostListView(ListView):
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        queryset = Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-publish')

        # Поиск
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query)
            )

        # Фильтрация по категории
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Фильтрация по автору
        author_id = self.request.GET.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['search_query'] = self.request.GET.get('search', '')
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'

    def get_queryset(self):
        return Post.objects.filter(status=Post.Status.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        # Увеличиваем счетчик просмотров
        post.increment_views()

        # Добавляем форму комментария
        context['comment_form'] = CommentForm()
        context['comments'] = post.comments.filter(active=True)

        # Похожие посты
        context['similar_posts'] = Post.objects.filter(
            status=Post.Status.PUBLISHED,
            category=post.category
        ).exclude(id=post.id)[:3]

        return context


class PostCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def test_func(self):
        return self.request.user.is_trainer

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Пост успешно создан!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/post_form.html'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_admin

    def form_valid(self, form):
        messages.success(self.request, 'Пост успешно обновлен!')
        return super().form_valid(form)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'posts/post_confirm_delete.html'
    success_url = reverse_lazy('posts:post_list')

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author or self.request.user.is_admin

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Пост успешно удален!')
        return super().delete(request, *args, **kwargs)


@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Ваш комментарий добавлен!')

    return redirect('posts:post_detail', slug=post.slug)


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user == comment.author or request.user.is_admin:
        comment.delete()
        messages.success(request, 'Комментарий удален!')

    return redirect('posts:post_detail', slug=comment.post.slug)