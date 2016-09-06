Deploying the site
==================

To deploy:

    git push heroku master
    heroku run python manage.py migrate
    manage.py collectstatic

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
