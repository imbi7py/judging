#from django.shortcuts import render
from django_twilio.decorators import twilio_view
from twilio import twiml
from models import (
    Judge,
    Team,
)


@twilio_view
def vote(request):
    judge = Judge.objects.get(phone=request.POST.get('From'))
    resp = request.POST.get('Body', '')
    r = twiml.Response()
    try:
        if len(resp) > 2:
            team, score = resp.split()
            team = Team.objecs.get(number=int(team))
            score = int(score)
        else:
            team = judge.current_team
            score = int(resp)
        judge.vote(team, score)
    except Exception as ex:
        r.message("vote failed: {0}".format(ex))
        return r
    judge = Judge.objects.get(id=judge.id)
    if judge.current_team:
        r.message("new team: {0}".format(judge.current_team.number))
    else:
        r.message("all done!")
    return r
