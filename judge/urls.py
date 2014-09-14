from django.conf.urls import patterns, url

from judge import views

urlpatterns = patterns(
    '',
    url(r'^twilio/$', views.vote, name='vote')
)
