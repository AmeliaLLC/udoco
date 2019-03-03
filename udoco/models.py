from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_delete
from django.dispatch import receiver
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

    def save(self, *args, **kwargs):
        if self.display_name == '':
            self.display_name = self.username
        if self.email == '':
            raise ValidationError(_('Email cannot be empty'))

        super(Official, self).save(*args, **kwargs)

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

    league = models.ForeignKey('League', on_delete=models.CASCADE)

    created = models.DateTimeField(_('created'), auto_now_add=True)
    creator = models.ForeignKey('Official', on_delete=models.CASCADE)

    complete = models.BooleanField(default=False)

    def get_absolute_url(self):
        if settings.DEBUG:
            root = 'http://local.udoco.org:8000'
        else:
            root = 'https://www.udoco.org'
        return '{}/games/{}'.format(root, self.id)

    @property
    def call_time(self):
        return self.start - timedelta(hours=1)

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
    def rostered(self):
        """Return all rostered officials."""
        rostered = []
        for roster in self.rosters.all():
            rostered += roster.officials
        return list(set(rostered))

    @property
    def emails(self):
        if self.complete:
            return [r.email for r in self.rostered]
        else:
            recipients = [
                official.email for official in self.applicants]
            recipients += [
                loser.email for loser in self.losers]
        return recipients


class ApplicationNotes(models.Model):
    """Notes for an application."""
    official = models.ForeignKey(
        Official, related_name='+', on_delete=models.CASCADE)
    game = models.ForeignKey(Game, related_name='+', on_delete=models.CASCADE)

    content = models.CharField(max_length=256, blank=True)


class ApplicationEntry(models.Model):
    """An application preference entry."""
    official = models.ForeignKey(
        Official, related_name='applicationentries', on_delete=models.CASCADE)
    game = models.ForeignKey(
        Game, related_name='applicationentries', on_delete=models.CASCADE)

    index = models.PositiveIntegerField()
    preference = models.PositiveIntegerField(
        choices=choices.OfficialPositions.choices)

    @property
    def name(self):
        return choices.OfficialPositions.choices[self.preference][1]

@receiver(pre_delete, sender=ApplicationEntry)
def unroster_officials(sender, **kwargs):
    """Unroster officials when their application is deleted."""
    obj = kwargs['instance']
    official = obj.official
    game = obj.game

    rosters = obj.game.rosters.filter(
        Q(hr=official) | Q(ipr=official) | Q(jr1=official) |
        Q(jr2=official) | Q(opr1=official) | Q(opr2=official) |
        Q(opr3=official) | Q(alt=official) | Q(jt=official) |
        Q(sk1=official) | Q(sk2=official) | Q(pbm=official) |
        Q(pbt1=official) | Q(pbt2=official) | Q(pt1=official) |
        Q(pt2=official) | Q(pw=official) | Q(iwb=official) |
        Q(lt1=official) | Q(lt2=official) | Q(so=official) |
        Q(hnso=official) | Q(nsoalt=official) | Q(ptimer=official)
    )
    for roster in rosters:
        for field in roster._meta.get_fields():
            if (type(field) is not models.ForeignKey or
                    field.related_model is not Official):
                continue
            name = field.name
            # We use == here instead of `is`, as the equality checks are
            # more correct in this case (memory versus database record).
            if getattr(roster, name) == official:
                # XXX: rockstar (3 Mar 2019) - This should emit an email to let
                # the staffers know.
                setattr(roster, name, None)
                roster.save()


class Loser(models.Model):
    """A 'User' that doesn't want to sign in."""

    # WARNING: email can't be unique here, because it gets created every
    # time a loser applies for a new game.
    derby_name = models.CharField(_('Derby name'), max_length=265, blank=False)
    email = models.EmailField(
        _('Email address'), blank=False)

    notes = models.CharField(max_length=256, blank=True)

    def __str__(self):
        return self.derby_name


class LoserApplicationEntry(models.Model):
    """An application for a Loser."""
    official = models.ForeignKey(
        Loser, related_name='applicationentries', on_delete=models.CASCADE)
    game = models.ForeignKey(
        Game, related_name='loserapplicationentries', on_delete=models.CASCADE)

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
        Game, related_name='rosters', on_delete=models.CASCADE)

    hr = models.ForeignKey(
        Official, related_name='hr_games', null=True, on_delete=models.SET_NULL)
    ipr = models.ForeignKey(
        Official, related_name='ipr_games', null=True,
        on_delete=models.SET_NULL)
    jr1 = models.ForeignKey(
        Official, related_name='jr1_games', null=True,
        on_delete=models.SET_NULL)
    jr2 = models.ForeignKey(
        Official, related_name='jr2_games', null=True,
        on_delete=models.SET_NULL)
    opr1 = models.ForeignKey(
        Official, related_name='opr1_games', null=True,
        on_delete=models.SET_NULL)
    opr2 = models.ForeignKey(
        Official, related_name='opr2_games', null=True,
        on_delete=models.SET_NULL)
    opr3 = models.ForeignKey(
        Official, related_name='opr3_games', null=True,
        on_delete=models.SET_NULL)
    alt = models.ForeignKey(
        Official, related_name='alt_games', null=True,
        on_delete=models.SET_NULL)

    jt = models.ForeignKey(
        Official, related_name="jt_games", null=True, on_delete=models.SET_NULL)
    sk1 = models.ForeignKey(
        Official, related_name="sk1_games", null=True,
        on_delete=models.SET_NULL)
    sk2 = models.ForeignKey(
        Official, related_name="sk2_games", null=True,
        on_delete=models.SET_NULL)
    pbm = models.ForeignKey(
        Official, related_name="pbm_games", null=True,
        on_delete=models.SET_NULL)
    pbt1 = models.ForeignKey(
        Official, related_name="pbt1_games", null=True,
        on_delete=models.SET_NULL)
    pbt2 = models.ForeignKey(
        Official, related_name="pbt2_games", null=True,
        on_delete=models.SET_NULL)
    pt1 = models.ForeignKey(
        Official, related_name="pt1_games", null=True,
        on_delete=models.SET_NULL)
    pt2 = models.ForeignKey(
        Official, related_name="pt2_games", null=True,
        on_delete=models.SET_NULL)
    pw = models.ForeignKey(
        Official, related_name="pw_games", null=True, on_delete=models.SET_NULL)
    iwb = models.ForeignKey(
        Official, related_name="iwb_games", null=True,
        on_delete=models.SET_NULL)
    lt1 = models.ForeignKey(
        Official, related_name="lt1_games", null=True,
        on_delete=models.SET_NULL)
    lt2 = models.ForeignKey(
        Official, related_name="lt2_games", null=True,
        on_delete=models.SET_NULL)
    so = models.ForeignKey(
        Official, related_name="so_games", null=True, on_delete=models.SET_NULL)
    hnso = models.ForeignKey(
        Official, related_name="hnso_games", null=True,
        on_delete=models.SET_NULL)
    nsoalt = models.ForeignKey(
        Official, related_name="nsoalt_games", null=True,
        on_delete=models.SET_NULL)
    ptimer = models.ForeignKey(
        Official, related_name="ptimer_games", null=True,
        on_delete=models.SET_NULL)

    # Losers
    hr_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    ipr_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    jr1_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    jr2_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    opr1_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    opr2_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    opr3_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    alt_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)

    jt_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    sk1_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    sk2_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    pbm_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    pbt1_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    pbt2_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    pt1_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    pt2_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    pw_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    iwb_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    lt1_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    lt2_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    so_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    hnso_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    nsoalt_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)
    ptimer_x = models.ForeignKey(
        Loser, related_name='+', null=True, on_delete=models.SET_NULL)

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
                if (type(field) is models.ForeignKey and
                        field.related_model is Official):
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
                if (type(field) is models.ForeignKey and
                        field.related_model is Loser):
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
