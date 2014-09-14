from django.db import models
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator
)
from django.core.mail import send_mail

from phonenumber_field.modelfields import PhoneNumberField
from django_twilio.client import twilio_client


# class Hackathon(models.Model):
#     judges = models.ManyToManyField("Judge")
#     teams = models.ManyToManyField("Team")


class Team(models.Model):
    name = models.CharField("Team Name", max_length=120)
    number = models.IntegerField("challengepost number")

    def average_score(self):
        votes = [vote.score for vote in Vote.objects.filter(team=self.id)]
        if len(votes) > 0:
            return sum(votes, 0.0)/len(votes)
        return 0

    def __str__(self):
        return "{0} - {1}".format(self.number, self.name)


class Judge(models.Model):
    name = models.CharField("Full Name", max_length=40)
    email = models.EmailField()
    phone = PhoneNumberField()
    current = models.ForeignKey(Team, blank=True, null=True)
    count = models.PositiveSmallIntegerField(blank=True, null=True)

    def __str__(self):
        return "{0}".format(self.name)

    def vote(self, score):
        Vote(judge=self, team=self.current, score=score).save()
        self.count += 1
        self.current = get_new_team()
        self.save()


def get_new_team():
    return None


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
            "{0} - You Were Added As A Judge, Congrats!",
            "You were added as a judge for {0}, text {1} to accept".format(
                "hackathon", "+16504818090"
            ),
            "judging@mlh.io",
            [instance.email],
            fail_silently=True
        )
        twilio_client.messages.create(
            body="Congrats you wee added as a judge",
            to=str(instance.phone),
            from_="+16504818090")


models.signals.post_save.connect(send_email, sender=Judge)
