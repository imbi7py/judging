from django.contrib import admin

from judge.models import (
    Team,
    Judge,
    Vote,
    Hackathon,
)


class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        import traceback
        print traceback.format_exc()


class HackathonAdmin(admin.ModelAdmin):
    class TeamsInline(admin.TabularInline):
        model = Team
        extra = 1
    inlines = [TeamsInline]


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'average_score')

    class VoteInline(admin.TabularInline):
        model = Vote
        extra = 1

    inlines = [VoteInline]


admin.site.register(Judge)
admin.site.register(Vote)
admin.site.register(Team, TeamAdmin)
admin.site.register(Hackathon, HackathonAdmin)
