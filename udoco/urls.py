from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.views.generic import TemplateView
from rest_framework_nested import routers

from udoco import views


router = routers.SimpleRouter(trailing_slash=False)
router.register('schedule', views.ScheduleViewSet)
router.register('league_schedule', views.LeagueScheduleViewSet)

router.register('events', views.EventViewSet)

events_router = routers.NestedSimpleRouter(router, r'events', lookup='event')
events_router.register(r'rosters', views.RosterViewSet)
events_router.register(r'applications', views.ApplicationViewSet)
events_router.register(r'lapplications', views.LoserApplicationViewSet)


admin.autodiscover()

urlpatterns = [
    url(r'^robots.txt', TemplateView.as_view(template_name='robots.txt')),
    url('^auth/', include('social_django.urls', namespace='social')),

    url(r'^api/', include(events_router.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api/me', views.me),

    url(r'^manage/contact', views.ContactLeaguesView.as_view(),
        name='contact_leagues'),
    url(r'^\.well-known/acme-challenge/(?P<public>.*)$',  # NOQA
        views.certbot_view),

    # Views outside the scope of this site, but required for functionality.
    url(r'^manage/', admin.site.urls),
    # Only needed for logout
    url('', include('django.contrib.auth.urls', namespace='auth')),

    url(r'^$', TemplateView.as_view(template_name='application.html'),
        name='index'),
    url(r'^.*/$', TemplateView.as_view(template_name='application.html'),
        name='index'),
]


if settings.MEDIA_ROOT.startswith('/'):
    from django.views.static import serve
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ]
