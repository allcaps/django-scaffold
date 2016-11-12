Django Scaffold
===============

Django Scaffold provides a build command to inspect models and generate views, urls, templates, admin etc.

Install
-------

    env/bin/pip install -e git+git@github.com:allcaps/django-scaffold.g#egg=django-scaffold


Usage
-----

Django Scaffold does introspection of `models.py`. Create a your webapp and compose your models.
Alternatively you can inspect an existing database with the
[inspectdb command](https://docs.djangoproject.com/en/1.10/howto/legacy-databases/).

Make sure both your app and `scaffold` are in `INSTALLED_APPS`:

    INSTALLED_APPS = [
        'your_app',
        'scaffold',
        ...
    ]


The `build` command generates admin, views, urls, templates and writes them to your app:

    python manage.py build your_app


After the build
---------------

# settings.py

    SITE_ID = 1

    TEMPLATES['OPTIONS']['context_processors'] += ['webapp.context_processors.base']

    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

    INSTALLED_APPS += ['django.contrib.sites']

# models.py

    from model_mixins import BaseMixin

    # For each model in models add BaseMixin:
    class Foo(BaseMixin, models.Model):


Creating your own scaffold
--------------------------

Make sure your app comes before `scaffold`. This makes Django find your template overrides first.

Copy the scaffold template to your_app/templates/scaffold to customise them:

    cp path/to/site-packages/scaffold/templates/scaffold your_app/templates/


Some ideas
----------

 - Override the django template processor to make a second template language to make 'template tempelates' more readable.
 - Create settings for Single and Multiple generator template names. So it is easy to customize the template sets.
 - Template packages (minimal, Bootstrap, REST API, CRUD, Wagtail).
 - Add get_admin_url and add admin edit buttons on page when user has access to admin.
 - Add instructions.html template to display in terminal.
 - Add rollback option or alternatively warn when project is not a clean checkout.
