from django.contrib import admin
from django.core import urlresolvers

from .models import Comic, Issue, Creator


class ComicAdmin(admin.ModelAdmin):
    list_display = ('title', 'issues', 'run', 'scraped', 'refreshed_at')
    list_filter = ('scraped', 'refreshed_at')
    search_fields = ('title',)


class IssueAdmin(admin.ModelAdmin):
    list_display = ('title', 'num', 'link_to_comic')

    def link_to_comic(self, obj):
        link=urlresolvers.reverse("admin:listing_comic_change", args=[obj.comic.id])
        return u'<a href="%s">%s</a>' % (link,obj.comic.title)
    link_to_comic.allow_tags=True


class CreatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'published_issues')


admin.site.register(Comic, ComicAdmin)
admin.site.register(Issue, IssueAdmin)
admin.site.register(Creator, CreatorAdmin)
