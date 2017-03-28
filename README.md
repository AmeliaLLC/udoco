Deploying the site
==================

To deploy:

    DATABASE_URL=sqlite:// GITREV=`git rev-parse --short HEAD` manage.py collectstatic --noinput
    git push heroku master
    heroku config:set GITVERSION=`git rev-parse --short HEAD`
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


Javascript toolchain
====================

The entire stack is run via `manage.py run`. That runs a grunt process that runs
`npm run watch` along with the the development server. It will build the files in
`static/application/**/*.css` as `static/app.css` and `static/application/**/*.js` as
`static/app.js`.

# TODO: Add information about how bower works to handle browserifying dependency
# assets.
