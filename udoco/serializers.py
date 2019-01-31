import functools

from django.utils import timezone
from rest_framework import serializers

from udoco import models


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.League
        fields = (
            'name',
            'abbreviation',
        )


class OfficialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Official
        fields = (
            'id',
            'display_name',
            'email',
            'phone_number',
            'game_history',
            'emergency_contact_name',
            'emergency_contact_number',
            'avatar',
            'league_affiliation',

            'league'
        )
    league = LeagueSerializer(read_only=True)


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Official
        fields = (
            'id',
            'display_name',
            'avatar',
            'league_affiliation',
            'preferences',
            'notes',
        )
    preferences = serializers.SerializerMethodField('_preferences')
    notes = serializers.SerializerMethodField('_notes')

    def _preferences(self, instance):
        game = self.context['game']
        entries = models.ApplicationEntry.objects.filter(
            official=instance, game=game).order_by('index')
        return [entry.name for entry in entries]

    def _notes(self, instance):
        game = self.context['game']
        try:
            notes = models.ApplicationNotes.objects.get(
                official=instance, game=game)
            return notes.content
        except models.ApplicationNotes.DoesNotExist:
            return ''


class LoserApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Loser
        fields = (
            'id',
            'derby_name',
            'preferences',
            'notes'
        )
    preferences = serializers.SerializerMethodField('_preferences')

    def _preferences(self, instance):
        game = self.context['game']
        entries = models.LoserApplicationEntry.objects.filter(
            official=instance, game=game).order_by('index')
        return [entry.name for entry in entries]


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Game
        fields = (
            'id',
            'title',
            'start',
            'location',
            'league',
            'complete',

            'has_applied',
            'can_apply',
            'is_authenticated',
            'can_schedule',
        )

    league = serializers.StringRelatedField()

    has_applied = serializers.SerializerMethodField('_has_applied')
    can_apply = serializers.SerializerMethodField('_can_apply')
    is_authenticated = serializers.SerializerMethodField('_is_authenticated')
    can_schedule = serializers.SerializerMethodField('_can_schedule')

    def _has_applied(self, instance):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return (models.ApplicationEntry.objects.filter(
            game=instance, official=user).count() > 0)

    def _can_apply(self, instance):
        return (bool(self.context['request'].user.is_authenticated) and not
                self._has_applied(instance) and not
                instance.complete and
                instance.start > timezone.now())

    def _can_schedule(self, instance):
        user = self.context['request'].user
        return (bool(user.is_authenticated) and
                user.league is not None and
                user.league.id == instance.league.id)

    # XXX: rockstar (20 Feb 2017) - Ugh ugh ugh.
    def _is_authenticated(self, instance):
        return bool(self.context['request'].user.is_authenticated)


class RosterSerializer(serializers.ModelSerializer):
    hr = serializers.SerializerMethodField('_hr')
    ipr = serializers.SerializerMethodField('_ipr')
    jr1 = serializers.SerializerMethodField('_jr1')
    jr2 = serializers.SerializerMethodField('_jr2')
    opr1 = serializers.SerializerMethodField('_opr1')
    opr2 = serializers.SerializerMethodField('_opr2')
    opr3 = serializers.SerializerMethodField('_opr3')
    alt = serializers.SerializerMethodField('_alt')
    jt = serializers.SerializerMethodField('_jt')
    sk1 = serializers.SerializerMethodField('_sk1')
    sk2 = serializers.SerializerMethodField('_sk2')
    pbm = serializers.SerializerMethodField('_pbm')
    pbt1 = serializers.SerializerMethodField('_pbt1')
    pbt2 = serializers.SerializerMethodField('_pbt2')
    pt1 = serializers.SerializerMethodField('_pt1')
    pt2 = serializers.SerializerMethodField('_pt2')
    pw = serializers.SerializerMethodField('_pw')
    iwb = serializers.SerializerMethodField('_iwb')
    lt1 = serializers.SerializerMethodField('_lt1')
    lt2 = serializers.SerializerMethodField('_lt2')
    so = serializers.SerializerMethodField('_so')
    hnso = serializers.SerializerMethodField('_hnso')
    nsoalt = serializers.SerializerMethodField('_nsoalt')
    ptimer = serializers.SerializerMethodField('_ptimer')

    def _get_serialized(key, instance):
        if getattr(instance, key) is not None:
            role = getattr(instance, key)
            return role.id
        elif getattr(instance, '{}_x'.format(key)) is not None:
            role = getattr(instance, '{}_x'.format(key))
            return 0 - role.id
        else:
            return None

    _hr = functools.partial(_get_serialized, 'hr')
    _ipr = functools.partial(_get_serialized, 'ipr')
    _jr1 = functools.partial(_get_serialized, 'jr1')
    _jr2 = functools.partial(_get_serialized, 'jr2')
    _opr1 = functools.partial(_get_serialized, 'opr1')
    _opr2 = functools.partial(_get_serialized, 'opr2')
    _opr3 = functools.partial(_get_serialized, 'opr3')
    _alt = functools.partial(_get_serialized, 'alt')

    _jt = functools.partial(_get_serialized, 'jt')
    _sk1 = functools.partial(_get_serialized, 'sk1')
    _sk2 = functools.partial(_get_serialized, 'sk2')
    _pbm = functools.partial(_get_serialized, 'pbm')
    _pbt1 = functools.partial(_get_serialized, 'pbt1')
    _pbt2 = functools.partial(_get_serialized, 'pbt2')
    _pt1 = functools.partial(_get_serialized, 'pt1')
    _pt2 = functools.partial(_get_serialized, 'pt2')
    _pw = functools.partial(_get_serialized, 'pw')
    _iwb = functools.partial(_get_serialized, 'iwb')
    _lt1 = functools.partial(_get_serialized, 'lt1')
    _lt2 = functools.partial(_get_serialized, 'lt2')
    _so = functools.partial(_get_serialized, 'so')
    _hnso = functools.partial(_get_serialized, 'hnso')
    _nsoalt = functools.partial(_get_serialized, 'nsoalt')
    _ptimer = functools.partial(_get_serialized, 'ptimer')

    class Meta:
        model = models.Roster
        fields = (
            'id',
            'hr',
            'ipr',
            'jr1',
            'jr2',
            'opr1',
            'opr2',
            'opr3',
            'alt',
            'jt',
            'sk1',
            'sk2',
            'pbm',
            'pbt1',
            'pbt2',
            'pt1',
            'pt2',
            'pw',
            'iwb',
            'lt1',
            'lt2',
            'so',
            'hnso',
            'nsoalt',
            'ptimer',
        )
