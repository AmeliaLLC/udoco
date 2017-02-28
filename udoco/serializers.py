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
            'display_name',
            'avatar',
            'league_affiliation',
            'preferences',
        )
    preferences = serializers.SerializerMethodField('_preferences')

    def _preferences(self, instance):
        event = self.context['event']
        entries = models.ApplicationEntry.objects.filter(
            official=instance, event=event).order_by('index')
        return [entry.name for entry in entries]


class GameSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Game
        fields = (
            'id',
            'title',
            'start',
            'end',
            'location',
            'league',
            'complete',

            'has_applied',
            'can_apply',
            'is_authenticated',
        )

    league = serializers.StringRelatedField()

    has_applied = serializers.SerializerMethodField('_has_applied')
    can_apply = serializers.SerializerMethodField('_can_apply')
    is_authenticated = serializers.SerializerMethodField('_is_authenticated')

    def _has_applied(self, instance):
        user = self.context['request'].user
        if not user.is_authenticated():
            return False
        return (models.ApplicationEntry.objects.filter(
            event=instance, official=user).count() > 0)

    def _can_apply(self, instance):
        return (self.context['request'].user.is_authenticated()
                and not self._has_applied(instance)
                and not instance.complete
                and instance.start > timezone.now())

    # XXX: rockstar (20 Feb 2017) - Ugh ugh ugh.
    def _is_authenticated(self, instance):
        return self.context['request'].user.is_authenticated()


class _RosteredSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Official
        fields = (
            'id',
            'display_name',
            'avatar',
            'league_affiliation',
        )


class RosterSerializer(serializers.ModelSerializer):
    hr = _RosteredSerializer(read_only=True)
    ipr = _RosteredSerializer(read_only=True)
    jr1 = _RosteredSerializer(read_only=True)
    jr2 = _RosteredSerializer(read_only=True)
    opr1 = _RosteredSerializer(read_only=True)
    opr2 = _RosteredSerializer(read_only=True)
    opr3 = _RosteredSerializer(read_only=True)
    alt = _RosteredSerializer(read_only=True)
    jt = _RosteredSerializer(read_only=True)
    sk1 = _RosteredSerializer(read_only=True)
    sk2 = _RosteredSerializer(read_only=True)
    pbm = _RosteredSerializer(read_only=True)
    pbt1 = _RosteredSerializer(read_only=True)
    pbt2 = _RosteredSerializer(read_only=True)
    pt1 = _RosteredSerializer(read_only=True)
    pt2 = _RosteredSerializer(read_only=True)
    pw = _RosteredSerializer(read_only=True)
    iwb = _RosteredSerializer(read_only=True)
    lt1 = _RosteredSerializer(read_only=True)
    lt2 = _RosteredSerializer(read_only=True)
    so = _RosteredSerializer(read_only=True)

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
        )
