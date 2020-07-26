from django.apps import AppConfig
from importlib import import_module
from .settings import get_var


class ControlledVocabularyConfig(AppConfig):
    name = "controlled_vocabulary"
    verbose_name = "Controlled Vocabulary"

    def ready(self):
        '''This is called by django when the project starts running.
        But before migrations (so the tables may not already exist!).
        '''
        import os

        root = get_var("DATA_ROOT")
        if not os.path.exists(root):
            os.mkdir(root)

        self.write_vocabulary_records_from_managers()

    @classmethod
    def get_vocabulary_manager(cls, prefix):
        '''Returns the vocabulary manager for the given vocabulary prefix.
        This is a unique instance (singleton).
        '''
        from django.apps import apps

        app = apps.get_app_config(cls.name)
        return app.vocabulary_managers.get(prefix, None)

    def write_vocabulary_records_from_managers(self):
        '''see _write_vocabulary_records_from_managers'''
        vocabulary_model = self._get_vocabulary_model()
        from .models import ControlledTerm
        return self._write_vocabulary_records_from_managers(
            vocabulary_model, ControlledTerm
        )

    def write_vocabulary_records_from_managers_during_migration(
        self, migration_apps
    ):
        '''
        see _write_vocabulary_records_from_managers().
        migration safe; migration_apps is the django app registry, see
        https://docs.djangoproject.com/en/3.0/topics/migrations/#data-migrations
        '''
        vocabulary_model = migration_apps.get_model(
            'controlled_vocabulary', 'ControlledVocabulary'
        )
        term_model = migration_apps.get_model(
            'controlled_vocabulary', 'ControlledTerm'
        )
        self._write_vocabulary_records_from_managers(
            vocabulary_model,
            term_model
        )

    def _write_vocabulary_records_from_managers(
        self, vocabulary_model, term_model
    ):
        """
        Create or update the ControlledVocabulary db records
        with metadata from the voc manager modules listed in
        settings.CONTROLLED_VOCABULARY_VOCABULARIES

        This method will always load the voc managers.

        'vocabulary_model' can be either None
        or <class 'controlled_vocabulary.models.ControlledVocabulary'>
        or <class '__fake__.ControlledVocabulary'> (from django migration)
        """
        from .models import ControlledTerm

        ret = self._load_vocabulary_managers()

        if vocabulary_model:
            for manager in ret.values():
                rec = {
                    "prefix": manager.prefix,
                    "label": manager.label,
                    "base_url": manager.base_url,
                    "description": manager.description,
                    "concept": ControlledTerm._get_or_create_from_code(
                        manager.concept, vocabulary_model, term_model
                    ),
                }

                vocabulary_model.objects.update_or_create(
                    prefix=rec["prefix"], defaults=rec
                )
        else:
            ret = None

        return ret

    def _load_vocabulary_managers(self):
        """
        Reset self.vocabulary_managers as a dictionary
        where prefix: <class>
        for each manager class specified in
        settings.CONTROLLED_VOCABULARY_VOCABULARIES
        """
        ret = self.vocabulary_managers = {}

        module_paths = get_var("VOCABULARIES")

        from .vocabularies.base import VocabularyBase as voc_base
        import inspect

        for path in module_paths:
            try:
                module = import_module(path)

            except ImportError:
                raise (
                    ImportError(
                        "{} not found (referenced from {} in your settings)".format(
                            path, "CONTROLLED_VOCABULARY_VOCABULARIES"
                        )
                    )
                )

            for name in dir(module):
                voc_class = getattr(module, name)
                if (
                    inspect.isclass(voc_class)
                    and issubclass(voc_class, voc_base)
                    and voc_class.prefix != "base"
                ):
                    ret[voc_class.prefix] = voc_class()

        return ret

    def _get_vocabulary_model(self):
        """Return the Vocabulary Django model (the class).
        None if not yet installed in the database (i.e. needs migration).
        """
        ret = None

        # Do NOT move this import outside this function
        from django.contrib.contenttypes.models import ContentType
        from django.db.utils import OperationalError, ProgrammingError

        try:
            ret = ContentType.objects.get(
                app_label=self.label, model="controlledvocabulary"
            ).model_class()
        except ContentType.DoesNotExist:
            # table doesn't exist yet
            pass
        except ProgrammingError:
            # django.db.utils.ProgrammingError: no such table:
            # django_content_type (e.g. postgresql)
            pass
        except OperationalError:
            # django.db.utils.OperationalError: no such table:
            # django_content_type (e.g. sqlite)
            pass

        return ret
