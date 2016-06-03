from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.shortcuts import render

from listing.models import Issue
from .models import ReadIssue


def read_issue(request, comic_id, issue_id):
    if not request.user:
        return HttpResponse('shuold be logged in for this to work, oh well')

    issue = Issue.objects.get(pk=issue_id)
    read, created = ReadIssue.objects.get_or_create(issue=issue, user=request.user)

    if created:
        read.count += 1

    read.save()
    return HttpResponse('captured read event')


def my_read(request):
    if not request.user:
        return HttpResponse('shuold be logged in for this to work, oh well')

    reads = ReadIssue.objects.filter(user=request.user)


def profile(request, pk):
    user = User.objects.get(pk=pk)

    reads = ReadIssue.objects.filter(user=user)

    return render(request, 'extras/profile.html', {'user': user, 'reads': reads})