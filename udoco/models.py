from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from udoco import choices


class Official(AbstractUser):
    """A representation of an official (or user) of the site."""
    verbose_name = _('Official')
    verbose_name_plural = _('Officials')
    # NOTE: rockstar (9 Jan 2016) - Django's default user allows email
    # to be blank and non-unique. That is insane.
    display_name = models.CharField(_('name'), max_length=256)

    game_history = models.URLField(blank=True)

    def __str__(self):
        return str(unicode(self))

    def __unicode__(self):
        if len(self.display_name) > 0:
            return self.display_name
        else:
            return u'{} {}'.format(
                self.first_name, self.last_name)

    def can_schedule(self):
        return self.scheduling.count() > 0


class League(models.Model):
    """A derby league."""
    verbose_name = _('League')
    verbose_name_plural = _('Leagues')

    name = models.CharField(_('league name'), max_length=255)
    abbreviation = models.CharField(_('league abbreviation'), max_length=5)

    created = models.DateTimeField(_('created'), auto_now_add=True)

    schedulers = models.ManyToManyField(Official, blank=True, related_name='scheduling')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Game(models.Model):
    """A derby game."""

    title = models.CharField(_('title'), max_length=1024)
    start = models.DateTimeField(_('game start'))
    end = models.DateTimeField(_('game end'))
    location = models.CharField(_('address'), max_length=1024)

    association = models.PositiveIntegerField(
        choices=choices.AssociationChoices.choices)
    game_type = models.PositiveIntegerField(
        choices=choices.GameTypeChoices.choices)

    league = models.ForeignKey('League')

    created = models.DateTimeField(_('created'), auto_now_add=True)
    creator = models.ForeignKey('Official')

#    available = models.ManyToManyField('Official', related_name='+')
#    staff = models.ManyToManyField('Official', related_name='games')

    def official_can_apply(self, official):
        return Application.objects.filter(game=self, official=official).count() == 0

    def can_schedule(self, official):
        return official in self.league.schedulers.all()


class Application(models.Model):
    """An application for a game."""

    official = models.ForeignKey(Official, related_name='applications')
    game = models.ForeignKey(Game, related_name='applications')

    so_first_choice = models.PositiveIntegerField(
        choices=choices.SkatingPositions.choices)
    so_second_choice = models.PositiveIntegerField(
        choices=choices.SkatingPositions.choices)
    so_third_choice = models.PositiveIntegerField(
        choices=choices.SkatingPositions.choices)

    nso_first_choice = models.PositiveIntegerField(
        choices=choices.NonskatingPositions.choices)
    nso_second_choice = models.PositiveIntegerField(
        choices=choices.NonskatingPositions.choices)
    nso_third_choice = models.PositiveIntegerField(
        choices=choices.NonskatingPositions.choices)
