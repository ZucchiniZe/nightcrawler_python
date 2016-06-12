from django.core.urlresolvers import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views import generic
from django.shortcuts import render

from django_q.tasks import async
from django_q.humanhash import humanize
from haystack.query import SearchQuerySet

from .models import Comic, Issue, Creator
from .tasks import scrape_titles, scrape_issues, scrape_creators
from .hooks import import_titles, import_issues, import_creators


class IndexView(generic.TemplateView):
    template_name = 'listing/frontpage.html'


class AllTitleView(generic.ListView):
    template_name = 'listing/listing.html'
    context_object_name = 'query'
    paginate_by = 100

    def get_queryset(self):
        return Comic.objects.all()


class SyncedView(generic.ListView):
    template_name = 'listing/listing.html'
    context_object_name = 'query'
    paginate_by = 100

    def get_queryset(self):
        return Comic.objects.filter(scraped=True)

    def get_context_data(self, **kwargs):
        context = super(SyncedView, self).get_context_data(**kwargs)
        context['synced'] = True
        return context


class AllCreatorView(generic.ListView):
    template_name = 'listing/creators.html'
    context_object_name = 'query'
    paginate_by = 155

    def get_queryset(self):
        return Creator.objects.all()


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
    messages.info(request, 'Refreshing comics. Please refresh in a few seconds. id: {0!s}'.format(id))
    return HttpResponseRedirect(reverse('listing:listing'))


def refresh_issues(request, pk):
    comic = Comic.objects.get(pk=pk)
    id = async(scrape_issues, pk, comic, hook=import_issues)
    id = humanize(id)
    messages.info(request, 'Refreshing issues for {0!s} Please refresh in a few seconds. id: {1!s}'.format(comic.title, id))
    return HttpResponseRedirect(reverse('listing:comic', args=(pk,)))


def refresh_creators(request):
    id = async(scrape_creators, hook=import_creators)
    id = humanize(id)
    messages.info(request, 'Refreshing creators. Please refresh in a few seconds. id: {0!s}'.format(id))
    return HttpResponseRedirect(reverse('listing:creators'))


def search(request):
    if 'q' in request.GET:
        results = SearchQuerySet().raw_search(request.GET['q'])
        return render(request, 'listing/search.html', {'results': results, 'query': request.GET['q']})
    else:
        return render(request, 'listing/search.html')
