from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django_q.tasks import async

from .models import Comic, Issue, Creator
from .scrape import scrape_titles, scrape_issues
from .hooks import import_titles, import_issues


def index(request):
    query = Comic.objects.all()
    return render(request, 'listing/index.html', {'query': query})


def comic(request, pk):
    comic = get_object_or_404(Comic, pk=pk)
    return render(request, 'listing/comic.html', {'comic': comic})


def issue(request, pk):
    issue = get_object_or_404(Issue, pk=pk)
    return render(request, 'listing/issue.html', {'issue': issue})


def creator(request, pk):
    creator = get_object_or_404(Creator, pk=pk)
    return render(request, 'listing/creator.html', {'creator': creator})


def refresh_comics(request):
    id = async(scrape_titles, hook=import_titles)
    return HttpResponse(id)


def refresh_issues(request, pk):
    comic = Comic.objects.get(pk=pk)
    id = async(scrape_issues, pk, comic, hook=import_issues)
    return HttpResponse(id)
