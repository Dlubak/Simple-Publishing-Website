# Create your views here.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .decorators import check_owner_or_admin
from .forms import ArticleForm, CommentForm
from .models import Article, Comment


def index(request):
    template_name = 'blog/index.html'
    context = {}
    all_articles = Article.objects.all().order_by('-pub_date')
    try:
        context['featured_article'] = all_articles[0]
        articles = all_articles[1:]
    except IndexError:
        articles = all_articles
    paginator = Paginator(articles, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context['page_obj'] = page_obj
    return render(request, template_name, context)


def article(request, article_id):
    template_name = 'blog/article.html'
    article = get_object_or_404(Article, id=article_id)
    session_key = f"article_{article_id}"
    if (not request.session.get(session_key)
            and request.user != article.author):
        article.views += 1
        article.save()
        request.session[session_key] = True
    form = CommentForm()
    if request.method != 'POST':
        form = CommentForm()
    else:
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = Comment(
                author=request.user,
                body=form.cleaned_data["body"],
                post=article
            )
            comment.save()
    post_comments = Comment.objects.filter(post=article)
    context = {
        'article': article,
        'comments': post_comments,
        'form': form
    }
    return render(request, template_name, context)


@login_required(login_url='/login')
def new_article(request):
    template_name = 'blog/new_article.html'

    if request.method != 'POST':
        articleForm = ArticleForm()
    else:
        articleForm = ArticleForm(data=request.POST, files=request.FILES)
        if articleForm.is_valid():
            new_article = articleForm.save(commit=False)
            new_article.author = request.user
            new_article.save()
            return redirect('blog:article', new_article.id)
    context = {'form': articleForm}
    return render(request, 'blog/new_article.html', context)


@check_owner_or_admin
@login_required(login_url='/login')
def edit_article(request, article_id):
    template_name = 'blog/edit.article.html'
    article = get_object_or_404(Article, id=article_id)
    if request.method != 'POST':
        form = ArticleForm(instance=article)
    else:
        form = ArticleForm(
            instance=article, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect('blog:article', article_id=article.id)
    context = {'form': form, 'article': article}
    return render(request, 'blog/edit_article.html', context)


@check_owner_or_admin
@login_required(login_url='/login')
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    author = article.author
    article.delete()
    return redirect('authentication:profile', username=author.username)


def search_article(request):
    search_post = request.GET.get('query')
    if search_post:
        articles = Article.objects.filter(
            Q(title__icontains=search_post) | Q(content__icontains=search_post))
    else:
        articles = Article.objects.all().order_by("-pub_date")

    paginator = Paginator(articles, 4)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template_name = 'blog/index.html'
    context = {'page_obj': page_obj}
    return render(request, template_name, context)
