from datetime import timedelta
import logging

import factory
import factory.fuzzy
from django.utils import timezone

from udoco import models

logger = logging.getLogger('factory')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.WARNING)


class OfficialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Official
    display_name = factory.fuzzy.FuzzyText(prefix='Official ')
    username = factory.fuzzy.FuzzyText(prefix='user-')
    email = factory.fuzzy.FuzzyText(suffix='@example.com')


class LeagueFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.League
    name = factory.fuzzy.FuzzyText(prefix='league-')


class GameFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Game
    title = factory.fuzzy.FuzzyText(prefix='Game ')
    start = factory.fuzzy.FuzzyDateTime(
        start_dt=timezone.now() + timedelta(days=1),
        end_dt=timezone.now() + timedelta(days=10))

    association = factory.fuzzy.FuzzyInteger(0, 2)
    game_type = factory.fuzzy.FuzzyInteger(0, 1)

    creator = factory.SubFactory(OfficialFactory)
    league = factory.SubFactory(LeagueFactory)


class RosterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Roster

    game = factory.SubFactory(GameFactory)


class ApplicationNotesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ApplicationNotes
    official = factory.SubFactory(OfficialFactory)
    game = factory.SubFactory(GameFactory)
    content = factory.fuzzy.FuzzyText(prefix='I have notes')


class ApplicationEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ApplicationEntry
    official = factory.SubFactory(OfficialFactory)
    game = factory.SubFactory(GameFactory)
    index = factory.fuzzy.FuzzyInteger(1)
    preference = factory.fuzzy.FuzzyChoice(
        tuple([x for x in range(0, 16)]))


class LoserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Loser
    derby_name = factory.fuzzy.FuzzyText()
    email = factory.fuzzy.FuzzyText(prefix='loser@')


class LoserApplicationEntryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LoserApplicationEntry
    official = factory.SubFactory(LoserFactory)
    game = factory.SubFactory(GameFactory)
    index = factory.fuzzy.FuzzyInteger(1)
    preference = factory.fuzzy.FuzzyChoice(
        tuple([x for x in range(0, 16)]))
