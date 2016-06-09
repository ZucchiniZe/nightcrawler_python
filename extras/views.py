import json
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views import generic
from django.core.serializers import serialize

from haystack.query import SearchQuerySet
from haystack.inputs import Raw

from listing.models import Issue
from .models import ReadIssue, Playlist, PlaylistItem
from .forms import PlaylistForm


def read_issue(request, comic_id, issue_id):
    if not request.user.is_authenticated():
        return HttpResponse('should be logged in for this to work, oh well')

    issue = Issue.objects.get(pk=issue_id)
    read, created = ReadIssue.objects.get_or_create(issue=issue, user=request.user)

    read.count += 1

    read.save()
    return HttpResponse('captured read event')


def profile(request, pk):
    user = User.objects.get(pk=pk)

    reads = ReadIssue.objects.filter(user=user)

    return render(request, 'extras/profile.html', {'user': user, 'reads': reads})


class PlaylistListView(generic.ListView):
    model = Playlist
    template_name = 'extras/playlist_listing.html'
    paginate_by = 50


class PlaylistView(generic.DetailView):
    model = Playlist
    template_name = 'extras/playlist_detail.html'


def search_issues(request):
    results = SearchQuerySet().filter(type='issue', content=Raw(request.GET.get('q', '')))
    data = list(map(lambda x: dict(id=int(x.pk), **x.get_stored_fields()), results))
    return JsonResponse(data, safe=False)


def edit_playlist(request, pk):
    playlist = Playlist.objects.get(pk=pk)
    form = PlaylistForm(request.POST or None, instance=playlist)
    if form.is_valid():
        for item in request.POST.getlist('items'):
            pitem, created = PlaylistItem.objects.get_or_create(playlist=playlist, issue=Issue.objects.get(pk=item))
            pitem.save()
    items = serialize('json', playlist.items.all())
    return render(request, 'extras/playlist_edit.html', {'playlist': playlist, 'form': form, 'items': items})
