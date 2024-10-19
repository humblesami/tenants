from django.db.models import Q
from .models import Tag, Article
from django_tenants.utils import remove_www
from django.shortcuts import render, get_object_or_404


def home(request):
    hostname_without_port = remove_www(request.get_host().split(':')[0])
    # feature articles on the home page
    featured = Article.articlemanager.filter(featured=True)[0:3]

    context = {
        'name': hostname_without_port,
        'articles': featured
    }

    return render(request, 'index.html', context)


def articles(request):

    # get query from request
    query = request.GET.get('query')
    # print(query)
    # Set query to '' if None
    if not query:
        query = ''

    # stories = Article.articlemanager.all()
    # search for query in headline, sub headline, body
    stories = Article.articlemanager.filter(
        Q(headline__icontains=query) |
        Q(sub_headline__icontains=query) |
        Q(body__icontains=query)
    )
    tags = Tag.objects.all()
    context = {
        'articles': stories,
        'tags': tags,
    }
    return render(request, 'articles.html', context)


def article(request, story):
    res = get_object_or_404(Article, slug=story, status='published')
    context = {
        'article': res
    }
    return render(request, 'article.html', context)
