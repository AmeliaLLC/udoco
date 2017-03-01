from fabric.api import local


def staticupload():
    local(
        'DATABASE_URL=sqlite:// GITVERSION=`git rev-parse --short HEAD` '
        'manage.py collectstatic --noinput')


def migrate():
    local('heroku run python manage.py migrate')


def deploy():
    staticupload()
    local('heroku config:set GITVERSION=`git rev-parse --short HEAD`')
    local('git push heroku master')
    migrate()
