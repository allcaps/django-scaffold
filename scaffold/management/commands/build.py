# -*- coding: utf-8 -*-
import logging
import os

from django.conf import settings
from django.core.management import BaseCommand
from django.apps import apps
from django.core.management import CommandError
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.db import models

logger = logging.getLogger(__name__)


class BaseGenerator(object):
    template_names = []

    def __init__(self, context, path):
        self.context = context
        self.path = path

    def get_destination(self, template_name, app_name="", model_name=""):
        destination = self.path + template_name.replace(
            'scaffold/', '/'
        ).replace(
            '.py.html', '.py'
        ).replace(
            'APP_NAME', app_name
        ).replace(
            'MODEL_NAME', model_name
        )

        # Create the directory if it does not exist.
        directory = os.path.dirname(destination)
        if not os.path.exists(directory):
            os.makedirs(directory)

        return destination

    def generate(self):
        for template_name in self.template_names:
            template = get_template(template_name)
            data = template.render(self.context)
            destination = self.get_destination(template_name, app_name=self.context['app_name'])
            with open(destination, 'wb') as out:
                out.write(data.encode('utf-8'))
                logger.info(u"Write %s", destination)


class SingleFileGenerator(BaseGenerator):
    """SingeFileGenerator uses the complete context (all models) per template."""
    template_names = [
        'scaffold/admin.py.html',
        'scaffold/context_processors.py.html',
        'scaffold/model_mixins.py.html',
        'scaffold/static/APP_NAME/styles.css',
        'scaffold/templates/APP_NAME/index.html',
        'scaffold/templates/APP_NAME/pagination.html',
        'scaffold/templates/base.html',
        'scaffold/templatetags/__init__.py',
        'scaffold/templatetags/APP_NAME_tags.py',
        'scaffold/urls.py.html',
        'scaffold/views.py.html',
    ]


class MultiFileGenerator(BaseGenerator):
    """MultiFileGenerator splits the context into a context for each model. It generates multiple files per model."""
    template_names = [
        'scaffold/templates/APP_NAME/MODEL_NAME_base.html',
        'scaffold/templates/APP_NAME/MODEL_NAME_confirm_delete.html',
        'scaffold/templates/APP_NAME/MODEL_NAME_detail.html',
        'scaffold/templates/APP_NAME/MODEL_NAME_form.html',
        'scaffold/templates/APP_NAME/MODEL_NAME_list.html',
        'scaffold/templates/APP_NAME/MODEL_NAME_table_detail.html',
        'scaffold/templates/APP_NAME/MODEL_NAME_table_list.html',
    ]

    def generate(self):
        for obj in self.context['items']:
            date_template_names = []
            if obj['date_fields']:
                date_template_names = [
                    'scaffold/templates/APP_NAME/MODEL_NAME_archive.html',
                    'scaffold/templates/APP_NAME/MODEL_NAME_archive_day.html',
                    'scaffold/templates/APP_NAME/MODEL_NAME_archive_month.html',
                    'scaffold/templates/APP_NAME/MODEL_NAME_archive_week.html',
                    'scaffold/templates/APP_NAME/MODEL_NAME_archive_year.html',
                ]
            for template_name in self.template_names + date_template_names:
                template = get_template(template_name)
                data = template.render(obj)
                destination = self.get_destination(template_name, obj['app_name'], obj['url_name'])
                with open(destination, 'w') as out:
                    out.write(data)
                    logger.debug("Write %s", destination)


class Command(BaseCommand):
    """The handle method is executed by the `./manage.py build app_name` command.

    Introspect all models in the given app and call generators.

    The get fields methods are loosely based on:
    https://docs.djangoproject.com/en/1.10/ref/models/meta/
    """

    def add_arguments(self, parser):
        parser.add_argument('app_name', nargs='+', type=str)

    def get_fields(self, model):
        """All model fields, fields dynamically added from the other end excluded.

        `include_hidden` is False by default. If set to True, get_fields() will include fields that are used to
        back other field’s functionality. This will also include any fields that have a related_name (such as
        ManyToManyField, or ForeignKey) that start with a `+`."""
        return [field.name for field in model._meta.get_fields(include_hidden=False)]

    def get_concrete_fields(self, model):
        """All model fields, like get_fields but NO backward related fields."""
        fields = [
                (f, f.model if f.model != model else None)
                for f in model._meta.get_fields()
                if f.concrete and (
                    not f.is_relation
                    or f.one_to_one
                    or (f.many_to_one and f.related_model)
                )
            ]
        return [field.name for field, model in fields]

    def get_related_fields(self, model):
        """Related fields like ForeignKey, OneToOne fields."""
        return [
            field.name
            for field in model._meta.get_fields()
            if (field.one_to_many or field.one_to_one)
            and field.auto_created and not field.concrete
        ]

    def get_many_to_many_fields(self, model):
        """ManyToMany fields"""
        return [
            field.name
            for field in model._meta.get_fields()
            if field.many_to_many and not field.auto_created
        ]

    def get_date_fields(self, model):
        """Date or datetime fields"""
        return [
            field.name for field in model._meta.get_fields()
            if field.__class__ in (models.DateField, models.DateTimeField)
        ]

    def get_text_fields(self, model):
        """Text fields"""
        return [
            field.name for field in model._meta.get_fields()
            if field.__class__ in (models.CharField, models.TextField)
        ]

    def get_related_with_models(self, model):
        fields = [
            (f.related_model.__name__, f.model if f.model != model else None)
            for f in model._meta.get_fields()
            if (f.one_to_many or f.one_to_one)
            and f.auto_created and not f.concrete
            ]
        return list(set([model_name for model_name, _ in fields]))

    def handle(self, *args, **options):
        """Handle the command"""

        # Raise error if app is not in INSTALLED_APPS.
        app_name = options['app_name'][0]
        if app_name not in settings.INSTALLED_APPS:
            raise CommandError('Add {} to installed apps'.format(app_name))

        # Build one big context of all models and their fields.
        context = {'items': [], 'app_name': app_name}
        all_models = apps.all_models[app_name]
        for name, model in all_models.items():
            if "_" not in name:  # Django auto generated cross tables do have `_`. Exclude them.
                context['items'].append({
                    'app_name': app_name,
                    'model': model,
                    'model_name': model.__name__,
                    'url_name': slugify(model._meta.verbose_name).replace('-', ''),
                    'model_slug': slugify(model._meta.verbose_name).replace('-', ''),
                    'verbose_name': model._meta.verbose_name,
                    'verbose_plural': model._meta.verbose_name,
                    'table_name': model._meta.db_table,
                    'slug': slugify(model._meta.verbose_name),
                    'slug_plural': slugify(model._meta.verbose_name),
                    'fields': self.get_fields(model),
                    'concrete_fields': self.get_concrete_fields(model),
                    'related_fields': self.get_related_fields(model),
                    'many_to_many_fields': self.get_many_to_many_fields(model),
                    'date_fields': self.get_date_fields(model),
                    'text_fields': self.get_text_fields(model),
                    'releated_with_models': self.get_related_with_models(model),
                })

        logger.info(context)
        print(context)

        path = apps.app_configs[app_name].path
        for generator in [
            SingleFileGenerator,
            MultiFileGenerator,
        ]:
            generator(context=context, path=path).generate()

        logger.info('Success!')
