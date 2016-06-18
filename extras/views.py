import json
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views import generic
from django.core.serializers import serialize
from django.core.urlresolvers import reverse
from django.contrib import messages

from haystack.query import SearchQuerySet
from haystack.inputs import Raw

from listing.models import Issue, Comic
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


def search_comics(request):
    results = SearchQuerySet().filter(type='comic', content=Raw(request.GET.get('q', '')))
    data = list(map(lambda x: dict(id=int(x.pk), **x.get_stored_fields()), results))
    return JsonResponse(data, safe=False)


def get_issues_comic(request, pk):
    comic = Comic.objects.get(pk=pk)
    issues = serialize('python', comic.issues.all())
    return JsonResponse(issues, safe=False)


def edit_playlist(request, pk=None):
    if pk is None and not request.is_ajax():
        return render(request, 'extras/playlist_edit.html', {'items': [], 'creating': True})

    if pk is None:
        playlist = Playlist()
    else:
        playlist = Playlist.objects.get(pk=pk)
        if request.user != playlist.creator:
            messages.error(request, 'You are not permitted to edit this playlist')
            return HttpResponseRedirect(reverse('extras:playlist', args=(pk,)))

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
                                                                    issue=Issue.objects.get(pk=item),
                                                                    defaults={'order': order})
            for item in PlaylistItem.objects.filter(playlist=playlist):
                if item.issue.id not in data.get('items'):
                    item.delete()

            return JsonResponse({'success': True, 'id': playlist.pk})
        else:
            return JsonResponse({
                'success': False,
                # as_json returns json as string, jsonresponse takes a dict and returns json
                'errors': json.loads(form.errors.as_json())
            })

    # get by playlistitem otherwise the ordering doesn't kick in
    items = serialize('json', [x.issue for x in playlist.playlistitem_set.all()])

    return render(request, 'extras/playlist_edit.html', {'playlist': playlist, 'items': items})


def delete_playlist(request, pk):
    playlist = Playlist.objects.get(pk=pk)
    if request.method == 'POST':
        if request.user != playlist.creator:
            messages.error(request, 'You are not permitted to edit this playlist')
            return HttpResponseRedirect(reverse('extras:playlist', args=(pk,)))
        else:
            playlist.delete()
            messages.success(request, 'Your playlist has been deleted.')
            return HttpResponseRedirect(reverse('extras:playlists'))
    elif request.method == 'GET':
        if request.user != playlist.creator:
            messages.error(request, 'You are not permitted to edit this playlist')
            return HttpResponseRedirect(reverse('extras:playlist', args=(pk,)))
        return render(request, 'extras/playlist_delete.html', {'playlist': playlist})
