"""udoco URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
#from rest_framework import routers
from rest_framework_nested import routers

from udoco import views


router = routers.SimpleRouter(trailing_slash=False)
router.register('leagues', views.LeagueViewSet)
router.register('officials', views.OfficialViewSet)

router.register('events', views.EventViewSet)

events_router = routers.NestedSimpleRouter(router, r'events', lookup='event')
events_router.register(r'rosters', views.RosterViewSet)
events_router.register(r'applications', views.ApplicationViewSet)


admin.autodiscover()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='udoco/index.html'),
        name='index'),
    url(r'^auth/', include('rest_framework_social_oauth2.urls')),
    url(r'^api/me', views.me),

    url(r'^leagues$', views.LeagueView.as_view(), name='leagues'),
    url(r'^leagues/edit$', views.EditLeagueView.as_view(), name='edit_leagues'),

    url(r'^events/new$', views.AddEventView.as_view(), name='add_event'),
    url(r'^events/(?P<event_id>[0-9]+)$',
        views.EventView.as_view(), name='view_event'),
    url(r'^events/(?P<event_id>[0-9]+)/edit$',
        views.AddEventView.as_view(), name='edit_event'),
    url(r'^events/(?P<event_id>[0-9]+)/delete$',
        views.EventDeleteView.as_view(),
        name='delete_event'),
    url(r'^events/(?P<event_id>[0-9]+)/withdraw$',
        views.EventWithdrawalView.as_view(),
        name='event_withdrawal'),
    url(r'^events/(?P<event_id>[0-9]+)/schedule$',
        views.SchedulingView.as_view(), name='schedule_event'),
    url(r'^events/(?P<event_id>[0-9]+)/schedule/commit$',
        views.CommitScheduleView.as_view(), name='commit_event'),

    url(r'^profile/edit$', views.ProfileView.as_view(), name='profile'),

    url(r'^api/', include(router.urls)),
    url(r'^api/', include(events_router.urls)),

    url(r'^_/events/(?P<event_id>[0-9]+)/withdraw',
        views._EventWithdrawView.as_view(), name='api_withdraw'),
    url(r'^_/events/(?P<event_id>[0-9]+)',
        views._EventView.as_view(), name='api_apply'),

    # Views outside the scope of this site, but required for functionality.
    url(r'^manage/', admin.site.urls),
    url('', include('django.contrib.auth.urls', namespace='auth')),
    url('', include('social.apps.django_app.urls', namespace='social')),
]


if settings.MEDIA_ROOT.startswith('/'):
    from django.views.static import serve
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ]
