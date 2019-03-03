from datetime import datetime
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'udoco.settings'  # NOQA
sys.path += ['.']  # NOQA

import subprocess

from django.conf import settings
from fabric.api import local
import requests

os.environ['AWS_ACCESS_KEY_ID'] = settings.AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = settings.AWS_SECRET_ACCESS_KEY


def test():
    local('coverage run --source=udoco manage.py test')
    local('coverage report --fail-under=92')
    local('flake8 --ignore=D100,D104 --exclude=udoco/migrations/* --max-line-length=80')


def manage_certs():
    """Generate a certificate."""
    update = True
    if not os.path.exists('certbot'):
        local('mkdir -p certbot')
        update = False

    local(
        'certbot --config-dir certbot --work-dir certbot --logs-dir '
        'certbot -d www.udoco.org certonly --manual'
    )

    if update:
        local('heroku certs:update --confirm udoco '
              'certbot/live/www.udoco.org/fullchain.pem '
              'certbot/live/www.udoco.org/privkey.pem')
    else:
        local('heroku certs:add certbot/live/www.udoco.org/fullchain.pem '
              'certbot/live/www.udoco.org/privkey.pem')


def staticupload():
    local(
        'DATABASE_URL=sqlite:// GITVERSION=`git rev-parse --short HEAD` '
        'manage.py collectstatic --noinput')


def migrate():
    local('heroku run python manage.py migrate')


def deploy_notify():
    """Notify telemetry about deployment."""
    try:
        os.environ['SENTRY_AUTH_TOKEN']
    except KeyError:
        print('No SENTRY_AUTH_TOKEN found in environment variables.')
        sys.exit(1)
    gitrev = subprocess.check_output(
        ['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
    payload = {
        'environment': 'production',
        'dateReleased': datetime.now().isoformat(),
        'version': gitrev,
        'ref': gitrev,
        'url': 'https://github.com/AmeliaLLC/udoco/commit/{}'.format(gitrev),
        'projects': [
            'udoco',
        ],
    }
    endpoint = 'https://sentry.io/api/0/organizations/{}/releases/'.format(  # NOQA
        'amelia-consulting')
    requests.post(
        endpoint,
        headers={
            'Authorization': 'Bearer {}'.format(
                os.environ['SENTRY_AUTH_TOKEN']),
            'Content-Type': 'application/json'
        },
        json=payload).raise_for_status()


def deploy():
    try:
        os.environ['REACT_APP_SENTRY_DSN']
    except KeyError:
        print('No REACT_APP_SENTRY_DSN found in environment variables.')
        sys.exit(1)
    local('git push origin')
    local('git push --tags origin')

    local('rm -f static/app.js static/app.css')
    local('cd frontend && npm install && npm run integrate')

    staticupload()
    local('heroku config:set GITVERSION=`git rev-parse --short HEAD`')
    local('heroku config:set SENTRY_DSN={}'.format(os.environ['SENTRY_DSN']))
    local('git push heroku master')
    migrate()
    deploy_notify()
