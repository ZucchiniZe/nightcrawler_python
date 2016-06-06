from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views import generic

from listing.models import Issue
from .models import ReadIssue, Playlist


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

