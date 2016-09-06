"""Social pipelines."""
from django.core.files.base import ContentFile
import requests


def save_profile_picture(
        strategy, user, response, details, is_new=False, *args,
        **kwargs):
    # XXX: rockstar (5 Sep 2016) - This should probably make sure
    # that we're actually talking about Facebook.
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
