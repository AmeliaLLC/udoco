Development toolchain
=====================

The backend uses Django, so you'll need to install the packages in `requirements.txt`
and `requirements-dev.txt`. How you do that is up to you (there are too many opinions).
The frontend uses React, so you'll need to install those dependencies with
`npm install`.

The entire stack is run via `manage.py run`. That starts a npm process that runs
`npm run watch` along with the the development server. It will build the application
in `frontend/src` into `static/app.js` and `static/app.css`. The only relevant
django templates are `templates/application.html` (the application itself) and
`templates/udoco/contact.html` (which should really be replaced with a admin view.

Deploying the site
==================

To deploy:

    DATABASE_URL=sqlite:// GITREV=`git rev-parse --short HEAD` manage.py collectstatic --noinput
    git push heroku master
    heroku config:set GITVERSION=`git rev-parse --short HEAD`
    heroku run python manage.py migrate

Updating certs
--------------

There is a task for updating the certs in `fab renew_cert`. A bunch of questions will
be asked of you, and then you'll be prompted to put some data on the server. Set
the key provided to `CERTBOT_KEY` in `settings` and then redeploy. At that time,
the key will be updated.

Create a superuser
==================

To create a new superuser, do `manage.py shell` pointed at the production database, and
then:

    from udoco.models import Official
    o = Official.objects.get(email=<email>)
    o.is_admin = True
    o.is_staff = True
    o.is_superuser = True
    o.save()

The user will now be able to navigate to udoco.org/manage to add leagues, etc.

Update to social
================

When updating to social-auth from python-social-auth, I had to do the following:

    $ echo "update django_migrations set app='social_django' where app='default';" | heroku pg:psql --app udoco
    $ heroku run python manage.py migrate social_django 0001 --fake
    $ heroku run python manage.py migrate social_django
