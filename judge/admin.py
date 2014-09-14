from django.contrib import admin

from judge.models import (
    Team,
    Judge,
    Vote
)


class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        import traceback
        print traceback.format_exc()


class VoteInline(admin.TabularInline):
    model = Vote
    extra = 1


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'average_score')
    inlines = [VoteInline]


admin.site.register(Team, TeamAdmin)
admin.site.register(Judge)
admin.site.register(Vote)
