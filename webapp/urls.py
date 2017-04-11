from django.conf.urls import patterns, include, url
from rest_framework.urlpatterns import format_suffix_patterns
from blackjack.views import PlayerList, PlayerDetail

from django.contrib import admin
admin.autodiscover()

# Webapp patterns
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', 'blackjack.views.api_root'),
    url(r'^players/$', PlayerList.as_view(), name='player-list'),
    url(r'^players/(?P<pk>[A-Za-z0-9-]+)/$', PlayerDetail.as_view(), name='player-detail'),
    url(r'^blackjack/', include('blackjack.urls')),
)

# Format suffixes
urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json', 'api'])

# Default login/logout views
urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)

