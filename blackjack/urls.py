from django.conf.urls import patterns, url
from blackjack.views import GameActionList, GameActionDetail

# Blackjack patterns
urlpatterns = patterns('',
    url(r'^gameactions/$', GameActionList.as_view(), name='gameaction-list'),
    url(r'^gameactions/(?P<pk>[A-Za-z0-9-]+)/$', GameActionDetail.as_view(), name='gameaction-detail'),
)