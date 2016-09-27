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

from udoco import views

admin.autodiscover()

urlpatterns = [
    url(r'^$', views.splash, name='index'),

    url(r'^leagues$', views.LeagueView.as_view(), name='leagues'),

    url(r'^events$', views.EventsView.as_view(), name='events'),
    url(r'^events/new$', views.AddEventView.as_view(), name='add_event'),
    url(r'^events/(?P<event_id>[0-9]+)$', views.EventView.as_view(), name='view_event'),
    url(r'^events/(?P<event_id>[0-9]+)/delete$',
        views.EventDeleteView.as_view(),
        name='delete_event'),
    url(r'^events/(?P<event_id>[0-9]+)/withdraw$',
        views.EventWithdrawalView.as_view(),
        name='event_withdrawal'),
    url(r'^events/(?P<event_id>[0-9]+)/schedule$', views.SchedulingView.as_view(),
        name='schedule_event'),

    url(r'^profile/edit$', views.ProfileView.as_view(), name='profile'),

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
