from django.test import TestCase
from .models import ControlledVocabulary, ControlledTerm
from django.core import management
from .apps import ControlledVocabularyConfig


class AnimalTestCase(TestCase):
    def setUp(self):
        management.call_command('vocab', 'init', verbosity=0)
        from django.apps import apps
        app = apps.get_app_config('controlled_vocabulary')
        app._load_vocabulary_managers()

    def test_vocab_init(self):
        '''Find built-in voc created by "vocab init"'''
        ControlledVocabulary.objects.get(
            prefix='iso639-2'
        )

    def test_term_create_from_code(self):
        '''Create new term & voc from code'''
        for i in range(2):
            ControlledTerm.get_or_create_from_code('avoc:123:My Term')

            ControlledTerm.objects.get(
                vocabulary__prefix='avoc',
                termid='123',
                label='My Term'
            )
