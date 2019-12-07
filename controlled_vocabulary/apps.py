from django.apps import AppConfig
from django.conf import settings
from importlib import import_module

# List of import paths to vocabularies lookup classes
# you can overwrite this in your Django settings.py
CONTROLLED_VOCABULARY_VOCABULARIES = [
    'controlled_vocabulary.vocabularies.iso639_2',
    'controlled_vocabulary.vocabularies.dcmitype',
    'controlled_vocabulary.vocabularies.schema',
    'controlled_vocabulary.vocabularies.mime',
    'controlled_vocabulary.vocabularies.fast_topic',
    'controlled_vocabulary.vocabularies.wikidata',
]


class ControlledVocabularyConfig(AppConfig):
    name = 'controlled_vocabulary'

    def ready(self):
        self._load_vocabulary_managers()

    @classmethod
    def get_vocabulary_manager(cls, prefix):
        from django.apps import apps
        app = apps.get_app_config(cls.name)
        return app.vocabulary_managers.get(prefix, None)

    def write_vocabulary_records_from_managers(self):
        from .models import ControlledTerm

        ControlledVocabulary = self._get_vocabulary_model()
        for manager in self.vocabulary_managers.values():
            rec = {
                'prefix': manager.prefix,
                'label': manager.label,
                'base_url': manager.base_url,
                'description': manager.description,
                'concept': ControlledTerm.get_or_create_from_code(
                    manager.concept
                ),
            }

            ControlledVocabulary.objects.update_or_create(
                prefix=rec['prefix'],
                defaults=rec
            )

        return self.vocabulary_managers

    def _load_vocabulary_managers(self):
        '''
        Create or Update the Vocabularies database records
        from the vocabularies found in the modules listed in
        settings.CONTROLLED_VOCABULARY_VOCABULARIES
        '''
        self.vocabulary_managers = {}

        ControlledVocabulary = self._get_vocabulary_model()
        if ControlledVocabulary is None:
            return

        vocabularies_settings_name = 'CONTROLLED_VOCABULARY_VOCABULARIES'

        module_paths = getattr(
            settings,
            vocabularies_settings_name,
            CONTROLLED_VOCABULARY_VOCABULARIES
        )

        from .vocabularies.base import VocabularyBase as voc_base
        import inspect

        for path in module_paths:
            try:
                module = import_module(path)

            except ImportError:
                raise(ImportError(
                    '{} not found (referenced from {} in your settings)'. format(
                        path,
                        vocabularies_settings_name
                    ))
                )

            for name in dir(module):
                voc_class = getattr(module, name)
                if inspect.isclass(voc_class) and issubclass(voc_class, voc_base) and voc_class.prefix != 'base':
                    self.vocabulary_managers[voc_class.prefix] = voc_class()

    def _get_vocabulary_model(self):
        '''Return the Vocabulary Django model (the class).
        None if not yet installed in the database (i.e. needs migration).
        '''
        ret = None

        # Do NOT move this import outside this function
        from django.contrib.contenttypes.models import ContentType
        try:
            ret = ContentType.objects.get(
                app_label=self.label,
                model='controlledvocabulary'
            ).model_class()
        except ContentType.DoesNotExist:
            pass

        return ret
