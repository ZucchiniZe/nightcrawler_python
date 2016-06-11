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

    if request.is_ajax() and request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        form = PlaylistForm(data)
        if form.is_valid():
            clean_data = {
                'title': form.cleaned_data.get('title'),
                'description': form.cleaned_data.get('description'),
                'creator': request.user,
            }
            playlist = Playlist(pk=playlist.pk, created_at=playlist.created_at, **clean_data)
            playlist.save()

            # use data for original order of ids, form.cleaned_data mucks up the order eliminating the purpose of this
            for order, item in enumerate(data.get('items')):
                pi, created = PlaylistItem.objects.update_or_create(playlist=playlist,
                                                                    issue=item,
                                                                    defaults={'order': order})

            return JsonResponse({'success': True})
        else:
            return JsonResponse({
                'success': False,
                'errors': json.loads(form.errors.as_json())
            })

    items = serialize('json', [x.issue for x in playlist.playlistitem_set.all()])

    return render(request, 'extras/playlist_edit.html', {'playlist': playlist, 'items': items})
