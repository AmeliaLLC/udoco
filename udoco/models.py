from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _

from udoco import choices, validators


class Official(AbstractUser):
    """A representation of an official (or user) of the site."""
    verbose_name = _('Official')
    verbose_name_plural = _('Officials')
    # NOTE: rockstar (9 Jan 2016) - Django's default user allows email
    # to be blank and non-unique. That is insane.
    display_name = models.CharField(_('name'), max_length=256)
    phone_number = models.CharField(
        validators=[validators.PHONE_NUMBER_VALIDATOR], blank=True, max_length=16)

    game_history = models.URLField(blank=True)

    emergency_contact_name = models.CharField(_('name'), max_length=256)
    emergency_contact_number = models.CharField(
        validators=[validators.PHONE_NUMBER_VALIDATOR], blank=True, max_length=16)

    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    official_type = models.PositiveIntegerField(
        choices=choices.OfficialType.choices, default=choices.OfficialType.ALL)
    league_affiliation = models.CharField(
        _('affiliation'), max_length=256, blank=True)

    def __str__(self):
        if len(self.display_name) > 0:
            return self.display_name
        else:
            return '{} {}'.format(
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

    def __unicode__(self):
        return unicode(self.official)

    def __str__(self):
        return str(self.official)


class Roster(models.Model):
    """A roster for an event."""

    game = models.OneToOneField(
        Game, on_delete=models.CASCADE, primary_key=True)

    hr = models.ForeignKey(Official, related_name='hr_games')
    ipr = models.ForeignKey(Official, related_name='ipr_games', null=True)
    jr1 = models.ForeignKey(Official, related_name='jr1_games')
    jr2 = models.ForeignKey(Official, related_name='jr2_games')
    opr1 = models.ForeignKey(Official, related_name='opr1_games', null=True)
    opr2 = models.ForeignKey(Official, related_name='opr2_games', null=True)
    opr3 = models.ForeignKey(Official, related_name='opr3_games', null=True)
    alt = models.ForeignKey(Official, related_name='alt_games', null=True)

    jt = models.ForeignKey(Official, related_name="jt_games", null=True)
    sk1 = models.ForeignKey(Official, related_name="sk1_games", null=True)
    sk2 = models.ForeignKey(Official, related_name="sk2_games", null=True)
    pbm = models.ForeignKey(Official, related_name="pbm_games", null=True)
    pbt1 = models.ForeignKey(Official, related_name="pbt1_games", null=True)
    pbt2 = models.ForeignKey(Official, related_name="pbt2_games", null=True)
    pt1 = models.ForeignKey(Official, related_name="pt1_games", null=True)
    pt2 = models.ForeignKey(Official, related_name="pt2_games", null=True)
    pw = models.ForeignKey(Official, related_name="pw_games", null=True)
    iwb = models.ForeignKey(Official, related_name="iwb_games", null=True)
    lt1 = models.ForeignKey(Official, related_name="lt1_games", null=True)
    lt2 = models.ForeignKey(Official, related_name="lt2_games", null=True)
