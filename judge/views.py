#from django.shortcuts import render
from django_twilio.decorators import twilio_view
from twilio import twiml
from models import Judge


@twilio_view
def vote(request):
    judge = Judge.objects.get(phone=request.POST.get('From'))
    resp = int(request.POST.get('Body', '1'))
    if len(resp) > 2:
        team, score = resp.split()
    r = twiml.Response()
    try:
        judge.vote(team, score)
    except Exception as ex:
        r.message("vote failed")
        print ex
        return r
    judge = Judge.objects.get(id=judge.id)
    if judge.current:
        r.message("new team: {0}".format(judge.current.number))
    else:
        r.message("all done!")
    return r
