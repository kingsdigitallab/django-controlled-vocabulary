from django.test import TestCase
from .models import ControlledVocabulary, ControlledTerm
from django.core import management
from .apps import ControlledVocabularyConfig


class ControlledVocTestCase(TestCase):

    @classmethod
    def setUpTestData(cls):
        management.call_command('vocab', 'init', verbosity=0)

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

    def test_search_term_or_none(self):
        '''search_term_or_none()'''
        prefix = 'wikidata'
        pattern_exact = 'pytest'
        pattern_partial = 'pytes'

        from .utils import search_term_or_none

        self.assertIsNone(search_term_or_none(prefix, None))
        self.assertIsNone(search_term_or_none(None, pattern_exact))
        self.assertIsNone(search_term_or_none(
            'does-not-exist', pattern_exact
        ))
        self.assertIsNone(search_term_or_none(
            prefix, 'does-not-exist-in-wikidata')
        )

        term = search_term_or_none(prefix, pattern_exact)
        self.assertEqual(pattern_exact, term.label)

        term = search_term_or_none(prefix, pattern_partial)
        self.assertEqual(pattern_exact, term.label)

        term = search_term_or_none(prefix, pattern_exact, exact=True)
        self.assertEqual(pattern_exact, term.label)

        term = search_term_or_none(prefix, pattern_partial, exact=True)
        self.assertIsNone(term)

        term = search_term_or_none(prefix, 'Q28975377', exact=True)
        self.assertEqual(pattern_exact, term.label)
