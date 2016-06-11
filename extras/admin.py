from django.contrib import admin

from ordered_model.admin import OrderedTabularInline

from .models import Playlist, PlaylistItem


class PlaylistItemInline(OrderedTabularInline):
    model = PlaylistItem
    fields = ('issue', 'playlist', 'order', 'move_up_down_links')
    readonly_fields = ('order', 'move_up_down_links')
    extra = 1
    ordering = ('order',)


class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'created_at')
    inlines = (PlaylistItemInline,)

    def get_urls(self):
        urls = super(PlaylistAdmin, self).get_urls()
        for inline in self.inlines:
            if hasattr(inline, 'get_urls'):
                urls = inline.get_urls(self) + urls
        return urls

admin.site.register(Playlist, PlaylistAdmin)
