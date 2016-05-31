from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import render

from django_q.tasks import async
from django_q.humanhash import humanize
from haystack.query import SearchQuerySet

from .models import Comic, Issue, Creator
from .tasks import scrape_titles, scrape_issues
from .hooks import import_titles, import_issues


class IndexView(generic.TemplateView):
    template_name = 'listing/frontpage.html'


class AllTitleView(generic.ListView):
    template_name = 'listing/listing.html'
    context_object_name = 'query'

    def get_queryset(self):
        return Comic.objects.all()


class SyncedView(generic.ListView):
    template_name = 'listing/listing.html'
    context_object_name = 'query'

    def get_queryset(self):
        return Comic.objects.filter(scraped=True)


class ComicView(generic.DetailView):
    model = Comic
    template_name = 'listing/comic.html'


class IssueView(generic.DetailView):
    model = Issue
    template_name = 'listing/issue.html'


class CreatorView(generic.DetailView):
    model = Creator
    template_name = 'listing/creator.html'


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


def search(request):
    if 'q' in request.GET:
        results = SearchQuerySet().raw_search(request.GET['q'])
        return render(request, 'listing/search.html', {'results': results, 'query': request.GET['q']})
    else:
        return render(request, 'listing/search.html')
