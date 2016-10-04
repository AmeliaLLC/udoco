from rest_framework import serializers

from udoco import models


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
            'official_type',
            'league_affiliation',
        )


class LeagueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.League
        fields = (
            'name',
            'abbreviation',
            'created',
            'email_template',
            'schedulers'
        )


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Game
        fields = (
            'title',
            'start',
            'end',
            'location',
            'association',
            'game_type',
            'league',
            'created',
            'creator',
            'complete',
        )


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
