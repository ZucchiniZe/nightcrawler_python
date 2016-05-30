from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.http import HttpResponseRedirect

from django_q.tasks import async
from django_q.humanhash import humanize
from haystack.generic_views import SearchView
from haystack.forms import SearchForm
from haystack.constants import DEFAULT_ALIAS
from haystack import connections

from .models import Comic, Issue, Creator
from .tasks import scrape_titles, scrape_issues
from .hooks import import_titles, import_issues


def index(request):
    return render(request, 'listing/frontpage.html')


def listing(request):
    query = Comic.objects.all()
    return render(request, 'listing/listing.html', {'query': query})


def synced(request):
    query = Comic.objects.filter(scraped=True)
    return render(request, 'listing/listing.html', {'query': query, 'synced': True})


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
    id = humanize(id)
    messages.info(request, 'Refreshing comics. Please refresh in a few seconds. id: %s' % id)
    return HttpResponseRedirect(reverse('listing:listing'))


def refresh_issues(request, pk):
    comic = Comic.objects.get(pk=pk)
    id = async(scrape_issues, pk, comic, hook=import_issues)
    id = humanize(id)
    messages.info(request, 'Refreshing issues for %s Please refresh in a few seconds. id: %s' % (comic.title, id))
    return HttpResponseRedirect(reverse('listing:comic', args=(pk,)))
