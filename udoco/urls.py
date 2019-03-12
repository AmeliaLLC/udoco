from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from rest_framework_nested import routers

from udoco import feeds, views


router = routers.SimpleRouter(trailing_slash=False)
router.register('schedule', views.ScheduleViewSet)
router.register('league_schedule', views.LeagueScheduleViewSet)

router.register('games', views.GameViewSet)

games_router = routers.NestedSimpleRouter(router, r'games', lookup='game')
games_router.register(r'rosters', views.RosterViewSet)
games_router.register(r'applications', views.ApplicationViewSet)
games_router.register(r'lapplications', views.LoserApplicationViewSet)


admin.autodiscover()

application = TemplateView.as_view(template_name='application.html')
urlpatterns = [
    url(r'^calendar/$', feeds.AllGameFeed()),
    url(r'^calendar/leagues/(?P<league_id>\d+)/$', feeds.LeagueGameFeed()),

    url(r'^robots.txt', TemplateView.as_view(
        template_name='robots.txt', content_type='text/plain')),
    url(r'^privacy', TemplateView.as_view(
        template_name='privacy.txt', content_type='text/plain')),
    url('^auth/',
        include(('social_django.urls', 'social_django'),
            namespace='social')),

    url(r'^api/', include(games_router.urls)),
    url(r'^api/', include(router.urls)),
    url(r'^api/me', views.me),
    url(r'^api/feedback', views.feedback),

    url(r'^manage/contact', views.ContactLeaguesView.as_view(),
        name='contact_leagues'),
    url(r'^\.well-known/acme-challenge/(?P<public>.*)$',  # NOQA
        views.certbot_view),
    url(r'^_email', views.email_hook),

    # Views outside the scope of this site, but required for functionality.
    url(r'^manage/', admin.site.urls),
    # Only needed for logout
    url(r'^/admin/',
        include(('django.contrib.auth.urls', 'admin'),
            namespace='auth')),
    url(r'^logout/$', auth_views.logout, name='logout'),

    # XXX: rockstar (28 Jan 2019) - Remove this url and the accompanying
    # view on or after 28 Apr 2019.
    url(r'^apply/(?P<game_id>\d+)/', views.redirect_old_apply_url),

    url(r'^$', application),
    url(r'^.*/$', application),

]


if settings.MEDIA_ROOT.startswith('/'):
    from django.views.static import serve
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    ]
