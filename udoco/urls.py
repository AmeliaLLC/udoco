from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from rest_framework_nested import routers

from udoco import views


router = routers.SimpleRouter(trailing_slash=False)
router.register('leagues', views.LeagueViewSet)
router.register('officials', views.OfficialViewSet)
router.register('schedule', views.ScheduleViewSet)

router.register('events', views.EventViewSet)

events_router = routers.NestedSimpleRouter(router, r'events', lookup='event')
events_router.register(r'rosters', views.RosterViewSet)
events_router.register(r'applications', views.ApplicationViewSet)
events_router.register(r'lapplications', views.LoserApplicationViewSet)


admin.autodiscover()

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='udoco/index.html'),
        name='index'),
    url('^auth/', include('social_django.urls', namespace='social')),

    url(r'^robots.txt', TemplateView.as_view(template_name='robots.txt')),
    url(r'^leagues$', views.LeagueView.as_view(), name='leagues'),
    url(r'^leagues/edit$', views.EditLeagueView.as_view(), name='edit_leagues'),

    url(r'^events/new$', views.AddEventView.as_view(), name='add_event'),
    url(r'^events/(?P<event_id>[0-9]+)$',
        views.EventView.as_view(), name='view_event'),
    url(r'^events/(?P<event_id>[0-9]+)/edit$',
        views.AddEventView.as_view(), name='edit_event'),
    url(r'^events/(?P<event_id>[0-9]+)/contact$',
        views.ContactEventView.as_view(), name='contact_officials'),
    url(r'^events/(?P<event_id>[0-9]+)/withdraw$',
        views.EventWithdrawalView.as_view(),
        name='event_withdrawal'),
    url(r'^events/(?P<event_id>[0-9]+)/schedule$',
        views.SchedulingView.as_view(), name='schedule_event'),
    url(r'^events/(?P<event_id>[0-9]+)/schedule/commit$',
        views.CommitScheduleView.as_view(), name='commit_event'),

    url(r'^profile/edit$', views.ProfileView.as_view(), name='profile'),

    url(r'^api/', include(events_router.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api/me', views.me),

    url(r'^_/events/(?P<event_id>[0-9]+)/withdraw',
        views._EventWithdrawView.as_view(), name='api_withdraw'),
    url(r'^_/events/(?P<event_id>[0-9]+)',
        views._EventView.as_view(), name='api_apply'),

    url(r'^manage/contact', views.ContactLeaguesView.as_view(),
        name='contact_leagues'),

    url(r'^\.well-known/acme-challenge/PgY0GMGX6kKAp6PLrheIeeYBFUrJL7E4Xke5UJTLQMI',  # NOQA
        TemplateView.as_view(template_name='certbot.txt')),

    url(r'^_.*$', TemplateView.as_view(template_name='application.html'),
        name='index_'),

    # Views outside the scope of this site, but required for functionality.
    url(r'^manage/', admin.site.urls),
    # Only needed for logout
    url('', include('django.contrib.auth.urls', namespace='auth')),
]


if settings.MEDIA_ROOT.startswith('/'):
    from django.views.static import serve
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ]
