import os
import subprocess
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'udoco.settings'
sys.path += ['.']

from django.conf import settings
from fabric.api import local
import requests

os.environ['AWS_ACCESS_KEY_ID'] = settings.AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = settings.AWS_SECRET_ACCESS_KEY

PROJECT_ID = '137988'
PROJECT_KEY = '08759bfe62310fbf1c03df886c525000'


def generate_cert():
    """Generate a certificate."""
    local('mkdir -p certbot')
    local(
        'certbot --config-dir certbot --work-dir certbot --logs-dir certbot '
        'certonly --manual'
    )
    local('heroku certs:add certbot/live/www.udoco.org/fullchain.pem '
          'certbot/live/www.udoco.org/privkey.pem')


def renew_cert():
    """Renew the cert."""
    local(
        'certbot --config-dir certbot --work-dir certbot --logs-dir certbot '
        'renew'
    )
    local('heroku certs:update certbot/live/www.udoco.org/fullchain.pem '
          'certbot/live/www.udoco.org/privkey.pem')


def staticupload():
    local(
        'DATABASE_URL=sqlite:// GITVERSION=`git rev-parse --short HEAD` '
        'manage.py collectstatic --noinput')


def migrate():
    local('heroku run python manage.py migrate')


def deploy_notify():
    """Notify Airbrake about deployment."""
    gitrev = subprocess.check_output(
        ['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
    payload = {
        'environment': 'production',
        'username': 'rockstar',
        'repository': 'https://github.com/AmeliaKnows.udoco',
        'revision': gitrev,
    }
    endpoint = 'https://airbrake.io/api/v4/projects/{}/deploys?key={}'.format(
        PROJECT_ID, PROJECT_KEY)
    requests.post(
        endpoint,
        headers={'Content-Type': 'application/json'},
        json=payload).raise_for_status()


def deploy():
    local('git push origin')

    staticupload()
    local('heroku config:set GITVERSION=`git rev-parse --short HEAD`')
    local('git push heroku master')
    migrate()
    deploy_notify()
