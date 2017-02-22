from django.utils import timezone
from rest_framework import serializers

from udoco import models


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.League
        fields = (
            'name',
            'abbreviation',
            'email_template',
        )


class OfficialSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Official
        fields = (
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


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Application
        fields = (
            'official',
            'game',
            'so_first_choice',
            'so_second_choice',
            'so_third_choice',
            'nso_first_choice',
            'nso_second_choice',
            'nso_third_choice',
        )


class RosterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Roster
        fields = (
            'game',
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
