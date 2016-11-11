Django Scaffold
===

Django app that provides a build command to inspect models and generates your admin, views, urls, templates etc.

Install
-------

    pip install [bitbucket here]


Usage
-----

Django Scaffold does introspection of you `models.py`. Write your models. 
 

Starting with a legacy database? Inspect your db with the (Django built-in) inspectdb command:

    python manage.py inspectdb > your_webapp/models.py


Make sure both `your_webapp` and `scaffold` are in `INSTALLED_APPS`:

    INSTALLED_APPS = [
        `your_webapp`,
        `django-scaffold`,
        ...
    ]

The `build` command generates admin, views, urls, templates:

    python manage.py build your_app


Customising the scaffold
------------------------

Make sure `your_webapp` comes before `django-scaffold`. This makes Django find your template overrides first.

Copy the Django Scaffold templates to your app to customise them:

    cp path/to/site-packages/django-scaffold/templates/scaffold your_webapp/templates/ 
