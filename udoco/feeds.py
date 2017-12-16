from django.conf import settings
from django.utils import timezone
from django_ical.views import ICalFeed

from udoco import models


class AbstractGameFeed(ICalFeed):
    """An abstract feed for handling all games."""

    timezone = settings.TIME_ZONE

    def item_title(self, item):
        return '{} presents "{}"'.format(item.league.name, item.title)

    def item_description(self, item):
        return 'Location: {}'.format(item.location)

    def item_start_datetime(self, item):
        return item.start


class AllGameFeed(AbstractGameFeed):
    """An iCal feed for listing all upcoming games."""

    title = 'UDO Colorado Upcoming Events'

    def items(self):
        return models.Game.objects.filter(start__gt=timezone.now())


class LeagueGameFeed(AbstractGameFeed):
    """An iCal feed for a single league's upcoming games."""

    def title(self, league):
        return '{} Upcoming events'.format(league.name)

    def get_object(self, request, league_id):
        return models.League.objects.get(id=league_id)

    def items(self, league):
        return models.Game.objects.filter(
            league=league, start__gt=timezone.now())
