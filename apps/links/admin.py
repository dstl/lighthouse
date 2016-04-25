# (c) Crown Owned Copyright, 2016. Dstl.
from django.contrib import admin

from .models import Link, LinkUsage


class LinkUsageAdmin(admin.ModelAdmin):
    readonly_fields = ('start', 'duration',)
    exclude = ('end',)


class LinkAdmin(admin.ModelAdmin):
    readonly_fields = ('added',)
    search_fields = ('name', 'description', 'destination',)


admin.site.register(Link, LinkAdmin)
admin.site.register(LinkUsage, LinkUsageAdmin)
