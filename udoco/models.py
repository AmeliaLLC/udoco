from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.db import models
from django.utils.translation import ugettext_lazy as _

from udoco import choices

PHONE_NUMBER_VALIDATOR = validators.RegexValidator(
    regex=r'^\+?1?\d{9,15}$',
    message=(
        "Phone number must be entered in the format: "
        "'+999999999'. Up to 15 digits allowed."))


class Official(AbstractUser):
    """A representation of an official (or user) of the site."""
    class Meta:
        ordering = ['display_name']

    verbose_name = _('Official')
    verbose_name_plural = _('Officials')
    email = models.EmailField(_('email address'), blank=False)
    display_name = models.CharField(_('name'), max_length=256)
    phone_number = models.CharField(
        validators=[PHONE_NUMBER_VALIDATOR], blank=True,
        max_length=16)

    game_history = models.URLField(blank=True)

    emergency_contact_name = models.CharField(_('name'), max_length=256)
    emergency_contact_number = models.CharField(
        validators=[PHONE_NUMBER_VALIDATOR], blank=True,
        max_length=16)

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

    # XXX: rockstar (17 Jan 2017) - This makes it impossible to schedule
    # for multiple leagues. I think that's okay, for now.
    @property
    def league(self):
        try:
            return self.scheduling.all()[0]
        except IndexError:
            return None


class League(models.Model):
    """A derby league."""
    verbose_name = _('League')
    verbose_name_plural = _('Leagues')

    name = models.CharField(_('league name'), max_length=255)
    abbreviation = models.CharField(_('league abbreviation'), max_length=5)

    created = models.DateTimeField(_('created'), auto_now_add=True)

    email_template = models.TextField(blank=True)

    schedulers = models.ManyToManyField(
        Official, blank=True, related_name='scheduling')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Game(models.Model):
    """A derby game."""

    title = models.CharField(_('title'), max_length=1024)
    start = models.DateTimeField(_('game start'))
    location = models.CharField(_('address'), max_length=1024)

    association = models.PositiveIntegerField(
        choices=choices.AssociationChoices.choices)
    game_type = models.PositiveIntegerField(
        choices=choices.GameTypeChoices.choices)

    league = models.ForeignKey('League')

    created = models.DateTimeField(_('created'), auto_now_add=True)
    creator = models.ForeignKey('Official')

    complete = models.BooleanField(default=False)

    def official_can_apply(self, official):
        return (
            not self.complete and
            ApplicationEntry.objects.filter(
                game=self, official=official).count() == 0)

    def can_schedule(self, official):
        return official in self.league.schedulers.all()

    @property
    def staff(self):
        ids = set()
        for roster in self.rosters.all():
            ids |= set([o.id for o in roster.officials])
        return Official.objects.filter(id__in=ids)

    @property
    def staffed_losers(self):
        ids = set()
        for roster in self.rosters.all():
            ids |= set([o.id for o in roster.losers])
        return Loser.objects.filter(id__in=ids)

    @property
    def nonrostered(self):
        return Official.objects.filter(
            applications__in=self.applications.all()).exclude(
            pk__in=[user.pk for user in self.staff])

    @property
    def applicants(self):
        return Official.objects.filter(
            applicationentries__in=self.applicationentries.all()).distinct()

    @property
    def losers(self):
        return Loser.objects.filter(
            applicationentries__in=self.loserapplicationentries.all()
        ).distinct()

    @property
    def emails(self):
        if self.complete:
            recipients = []
            for roster in self.rosters.all():
                recipients += roster.emails
        else:
            recipients = [
                official.email for official in self.applicants]
            recipients += [
                loser.email for loser in self.losers]
        return recipients


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


class ApplicationEntry(models.Model):
    """An application preference entry."""
    official = models.ForeignKey(Official, related_name='applicationentries')
    game = models.ForeignKey(
        Game, related_name='applicationentries')

    index = models.PositiveIntegerField()
    preference = models.PositiveIntegerField(
        choices=choices.OfficialPositions.choices)

    @property
    def name(self):
        return choices.OfficialPositions.choices[self.preference][1]


class Loser(models.Model):
    """A 'User' that doesn't want to sign in."""

    # WARNING: email can't be unique here, because it gets created every
    # time a loser applies for a new game.
    derby_name = models.CharField(_('Derby name'), max_length=265, blank=False)
    email = models.EmailField(
        _('Email address'), blank=False)

    def __str__(self):
        return self.derby_name


class LoserApplicationEntry(models.Model):
    """An application for a Loser."""
    official = models.ForeignKey(Loser, related_name='applicationentries')
    game = models.ForeignKey(
        Game, related_name='loserapplicationentries')

    index = models.PositiveIntegerField()
    preference = models.PositiveIntegerField(
        choices=choices.OfficialPositions.choices)

    @property
    def name(self):
        return choices.OfficialPositions.choices[self.preference][1]


class Roster(models.Model):
    """A roster for an game."""

    class Meta:
        ordering = ['id']

    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name='rosters')

    hr = models.ForeignKey(Official, related_name='hr_games', null=True)
    ipr = models.ForeignKey(Official, related_name='ipr_games', null=True)
    jr1 = models.ForeignKey(Official, related_name='jr1_games', null=True)
    jr2 = models.ForeignKey(Official, related_name='jr2_games', null=True)
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
    so = models.ForeignKey(Official, related_name="so_games", null=True)
    hnso = models.ForeignKey(Official, related_name="hnso_games", null=True)
    nsoalt = models.ForeignKey(Official, related_name="nsoalt_games", null=True)
    ptimer = models.ForeignKey(Official, related_name="ptimer_games", null=True)

    # Losers
    hr_x = models.ForeignKey(Loser, related_name='+', null=True)
    ipr_x = models.ForeignKey(Loser, related_name='+', null=True)
    jr1_x = models.ForeignKey(Loser, related_name='+', null=True)
    jr2_x = models.ForeignKey(Loser, related_name='+', null=True)
    opr1_x = models.ForeignKey(Loser, related_name='+', null=True)
    opr2_x = models.ForeignKey(Loser, related_name='+', null=True)
    opr3_x = models.ForeignKey(Loser, related_name='+', null=True)
    alt_x = models.ForeignKey(Loser, related_name='+', null=True)

    jt_x = models.ForeignKey(Loser, related_name='+', null=True)
    sk1_x = models.ForeignKey(Loser, related_name='+', null=True)
    sk2_x = models.ForeignKey(Loser, related_name='+', null=True)
    pbm_x = models.ForeignKey(Loser, related_name='+', null=True)
    pbt1_x = models.ForeignKey(Loser, related_name='+', null=True)
    pbt2_x = models.ForeignKey(Loser, related_name='+', null=True)
    pt1_x = models.ForeignKey(Loser, related_name='+', null=True)
    pt2_x = models.ForeignKey(Loser, related_name='+', null=True)
    pw_x = models.ForeignKey(Loser, related_name='+', null=True)
    iwb_x = models.ForeignKey(Loser, related_name='+', null=True)
    lt1_x = models.ForeignKey(Loser, related_name='+', null=True)
    lt2_x = models.ForeignKey(Loser, related_name='+', null=True)
    so_x = models.ForeignKey(Loser, related_name='+', null=True)
    hnso_x = models.ForeignKey(Loser, related_name='+', null=True)
    nsoalt_x = models.ForeignKey(Loser, related_name='+', null=True)
    ptimer_x = models.ForeignKey(Loser, related_name='+', null=True)

    @property
    def real_hr(self):
        return self.hr_x if self.hr_x else self.hr

    @property
    def real_ipr(self):
        return self.ipr_x if self.ipr_x else self.ipr

    @property
    def real_jr1(self):
        return self.jr1_x if self.jr1_x else self.jr1

    @property
    def real_jr2(self):
        return self.jr2_x if self.jr2_x else self.jr2

    @property
    def real_opr1(self):
        return self.opr1_x if self.opr1_x else self.opr1

    @property
    def real_opr2(self):
        return self.opr2_x if self.opr2_x else self.opr2

    @property
    def real_opr3(self):
        return self.opr3_x if self.opr3_x else self.opr3

    @property
    def real_alt(self):
        return self.alt_x if self.alt_x else self.alt

    @property
    def real_jt(self):
        return self.jt_x if self.jt_x else self.jt

    @property
    def real_sk1(self):
        return self.sk1_x if self.sk1_x else self.sk1

    @property
    def real_sk2(self):
        return self.sk2_x if self.sk2_x else self.sk2

    @property
    def real_pbm(self):
        return self.pbm_x if self.pbm_x else self.pbm

    @property
    def real_pbt1(self):
        return self.pbt1_x if self.pbt1_x else self.pbt1

    @property
    def real_pbt2(self):
        return self.pbt2_x if self.pbt2_x else self.pbt2

    @property
    def real_pt1(self):
        return self.pt1_x if self.pt1_x else self.pt1

    @property
    def real_pt2(self):
        return self.pt2_x if self.pt2_x else self.pt2

    @property
    def real_pw(self):
        return self.pw_x if self.pw_x else self.pw

    @property
    def real_iwb(self):
        return self.iwb_x if self.iwb_x else self.iwb

    @property
    def real_lt1(self):
        return self.lt1_x if self.lt1_x else self.lt1

    @property
    def real_lt2(self):
        return self.lt2_x if self.lt2_x else self.lt2

    @property
    def real_so(self):
        return self.so_x if self.so_x else self.so

    @property
    def real_hnso(self):
        return self.hnso_x if self.hnso_x else self.hnso

    @property
    def real_nsoalt(self):
        return self.nsoalt_x if self.nsoalt_x else self.nsoalt

    @property
    def real_ptimer(self):
        return self.ptimer_x if self.ptimer_x else self.ptimer

    @property
    def officials(self):
        ids = []
        for attr in dir(self.__class__):
            try:
                field = getattr(self.__class__, attr).field
                if (type(field) is models.ForeignKey
                        and field.related_model is Official):
                    val = getattr(self, attr)
                    if val is not None:
                        ids.append(val.id)
            except AttributeError:
                continue
        return Official.objects.filter(id__in=ids)

    @property
    def losers(self):
        ids = []
        for attr in dir(self.__class__):
            try:
                field = getattr(self.__class__, attr).field
                if (type(field) is models.ForeignKey
                        and field.related_model is Loser):
                    val = getattr(self, attr)
                    if val is not None:
                        ids.append(val.id)
            except AttributeError:
                continue
        return Loser.objects.filter(id__in=ids)

    @property
    def emails(self):
        emails = [user.email for user in self.officials]
        emails += [loser.email for loser in self.losers]
        return emails
