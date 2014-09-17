from django.utils.translation import ugettext as _
from django.db import models
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from phonenumber_field.modelfields import PhoneNumberField
from judging.settings import TWILIO_NUMBER
from django_twilio.client import twilio_client


class Hackathon(models.Model):
    name = models.CharField("Hackathon", max_length="90")
    date = models.DateTimeField()
    judges = models.ManyToManyField("Judge", blank=True, null=True)

    def __str__(self):
        return self.name


def get_new_team(hackathon, judge):
    assert type(hackathon) is Hackathon
    assert type(judge) is Judge
    teams = Team.objects.filter(
        hackathon=hackathon
    ).exclude(
        vote__judge=judge
    ).order_by('?').get()
    if len(teams) > 0:
        return teams[0].get()
    return None


class Team(models.Model):
    name = models.CharField("Team Name", max_length=120)
    number = models.IntegerField("Team Number")
    hackathon = models.ForeignKey("Hackathon")

    def average_score(self):
        votes = [vote.score for vote in Vote.objects.filter(team=self.id)]
        if len(votes) > 0:
            return sum(votes, 0.0)/len(votes)
        return 0

    def __str__(self):
        return "{0} - {1}".format(self.number, self.name)

    class Meta:
        unique_together = ("number", "hackathon")


class Judge(models.Model):
    user = models.OneToOneField(User)
    name = models.CharField("Full Name", max_length=40)
    email = models.EmailField()
    phone = PhoneNumberField()
    current_team = models.ForeignKey("Team", blank=True, null=True)
    remaining_votes = models.PositiveSmallIntegerField(blank=True, null=True)
    free_vote = models.BooleanField(default=False)
    current_hackathon = models.ForeignKey("Hackathon", blank=True, null=True)

    def __str__(self):
        return "{0}".format(self.name)

    def vote(self, team, score):
        if score < 1 or score > 10:
            raise ValidationError(_("Score out of bounds, 0-10."))
        if not self.free_voter and team != self.current_team:
            raise ValidationError(_("Can't vote freely."))
        Vote(judge=self, team=team, score=score).save()
        self.count += 1
        self.current_team = get_new_team()
        self.save()


class Vote(models.Model):
    vote_date = models.DateTimeField(auto_now=True)
    judge = models.ForeignKey("Judge")
    team = models.ForeignKey("Team")
    score = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ])

    class Meta:
        unique_together = ("judge", "team")


def send_email(sender, instance, created, **kwargs):
    if sender == Judge and created is True:
        send_mail(
            _("{0} - You Were Added As A Judge, Congrats!").format(
                instance.current_hackathon
            ),
            _("You were added as a judge for {0}, text {1} to accept").format(
                instance.current_hackathon,
                TWILIO_NUMBER
            ),
            "judging@mlh.io",
            [instance.email],
            fail_silently=True
        )
        twilio_client.messages.create(
            body=_("Congrats you were added as a judge"),
            to=str(instance.phone),
            from_=TWILIO_NUMBER
        )

models.signals.post_save.connect(send_email, sender=Judge)
