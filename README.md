Deploying the site
==================

To deploy:

    DATABASE_URL=sqlite:// GITREV=`git rev-parse --short HEAD` manage.py collectstatic --noinput
    git push heroku master
    heroku config:set GITREV=`git rev-parse --short HEAD`
    heroku run python manage.py migrate

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
