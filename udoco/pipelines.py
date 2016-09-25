"""Social pipelines."""
from django.core.files.base import ContentFile
import requests


def save_profile_picture(
        strategy, user, response, details, is_new=False, *args,
        **kwargs):
    if kwargs['backend'].name != 'facebook':
        raise Exception('unsupported authentication backend: {}'.format(
            kwargs['backend'].name))

    if not bool(user.avatar):
        url = 'https://graph.facebook.com/{}/picture'.format(
            response['id'])

        try:
            res = requests.request('GET', url, params={'type': 'large'})
            res.raise_for_status()
        except requests.HTTPError:
            pass
        else:
            user.avatar.save(
                '{}.jpg'.format(user.username),
                ContentFile(res.content))
