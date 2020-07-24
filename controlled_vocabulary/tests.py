from django.core import management
from django.test import TestCase

from .apps import ControlledVocabularyConfig
from .models import ControlledTerm, ControlledVocabulary


class ControlledVocTestCase(TestCase):
    '''
    python manage.py test controlled_vocabulary
    python manage.py test controlled_vocabulary.tests.ControlledVocTestCase.test_search_list_by_termid
    '''
    @classmethod
    def setUpTestData(cls):
        management.call_command("vocab", "init", verbosity=0)

    def test_vocab_init(self):
        '''Find built-in voc created by "vocab init"'''
        ControlledVocabulary.objects.get(prefix="iso639-2")

    def test_term_create_from_code(self):
        """Create new term & voc from code"""
        for i in range(2):
            ControlledTerm.get_or_create_from_code("avoc:123:My Term")

            ControlledTerm.objects.get(
                vocabulary__prefix="avoc", termid="123", label="My Term"
            )

    def test_search_term_or_none(self):
        """search_term_or_none()"""
        prefix = "wikidata"
        pattern_exact = "pytest"
        pattern_partial = "pytes"

        from .utils import search_term_or_none

        self.assertIsNone(search_term_or_none(prefix, None))
        self.assertIsNone(search_term_or_none(None, pattern_exact))
        self.assertIsNone(search_term_or_none("does-not-exist", pattern_exact))
        self.assertIsNone(search_term_or_none(prefix, "does-not-exist-in-wikidata"))

        term = search_term_or_none(prefix, pattern_exact)
        self.assertEqual(pattern_exact, term.label)

        term = search_term_or_none(prefix, pattern_partial)
        self.assertEqual(pattern_exact, term.label)

        term = search_term_or_none(prefix, pattern_exact, exact=True)
        self.assertEqual(pattern_exact, term.label)

        term = search_term_or_none(prefix, pattern_partial, exact=True)
        self.assertIsNone(term)

        term = search_term_or_none(prefix, "Q28975377", exact=True)
        self.assertEqual(pattern_exact, term.label)

        term = search_term_or_none(prefix, "q28975377", exact=True)
        self.assertEqual(pattern_exact, term.label)

        self.assertNotEqual("Essay", search_term_or_none("fast-topic", "Essay").label)
        self.assertEqual(
            "Essay", search_term_or_none("fast-topic", "Essay", exact=True).label
        )

    def test_search_lang_by_label(self):
        prefix = "iso639-2"

        manager = ControlledVocabularyConfig.get_vocabulary_manager(prefix)

        terms = manager.search("engl")
        # expect at least 'English', 'English, Middle', 'English, Old'
        self.assertGreater(len([t for t in terms if 'English' in t[1]]), 2)
        self.assertEqual(terms[0][1], 'English')

        terms = manager.search("german")
        # expect at least 'English', 'English, Middle', 'English, Old'
        self.assertGreater(len([t for t in terms if 'German' in t[1]]), 2)
        self.assertEqual(terms[0][1], 'German')
        self.assertEqual(terms[1][1], 'German')
        self.assertNotEqual(terms[0][0], terms[1][0])

    def test_search_lang_by_termid(self):
        '''base_list.search() should lookup termid as well as label
        See gh-8
        '''

        prefix = "iso639-2"
        termid = "glv"
        label = "Manx"

        # search by termid using the voc manager
        manager = ControlledVocabularyConfig.get_vocabulary_manager(prefix)

        terms = manager.search("fr")
        print(terms)

        # make sure we don't have that termid in the database already
        self.assertFalse(
            ControlledTerm.objects.filter(
                vocabulary__prefix=prefix, termid=termid
            ).exists()
        )

