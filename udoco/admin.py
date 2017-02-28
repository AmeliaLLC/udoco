from django.contrib import admin

from udoco import models


@admin.register(models.Official)
class OfficialAdmin(admin.ModelAdmin):
    """Admin for officials."""
    # TODO: we should handle scheduler promotion from the user, not
    # the league. Django makes setting that up very painful.

    def _display_name(obj):
        """Return the display name or first/last."""
        if obj.display_name:
            return obj.display_name
        else:
            return '{} {}'.format(
                obj.first_name, obj.last_name)
    list_display = (_display_name,)

    fieldsets = (
        (None, {
            'fields': (
                'display_name', 'first_name', 'last_name', 'email',
                'game_history',)}),
        ('Authorization', {
            'description': 'What are the user\'s capabilities?',
            'classes': ('collapse',),
            'fields': ('is_staff', 'is_active',)}))


@admin.register(models.League)
class LeagueAdmin(admin.ModelAdmin):
    """Admin for leagues."""
    def _schedulers(obj):
        return ', '.join([u.display_name for u in obj.schedulers.all()])
    list_display = ('name', _schedulers)

    fieldsets = (
        (None, {
            'fields': (
                'name', 'abbreviation',)}),
        ('Scheduling', {
            'description': 'The users with scheduling rights for this league.',
            'fields': (
                'schedulers',)}))


# Below are some dummy admin models to hide some boilerplate models.
from django.contrib.auth.models import Group
from social.apps.django_app.default.models import Association, Nonce, UserSocialAuth  # NOQA
from rest_framework.authtoken.models import Token
from oauth2_provider.models import AccessToken, Application, Grant, RefreshToken
admin.site.unregister(Group)
admin.site.unregister(Association)
admin.site.unregister(Nonce)
admin.site.unregister(UserSocialAuth)
admin.site.unregister(Token)
admin.site.unregister(AccessToken)
admin.site.unregister(Application)
admin.site.unregister(Grant)
admin.site.unregister(RefreshToken)
