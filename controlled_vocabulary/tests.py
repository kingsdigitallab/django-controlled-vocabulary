from django.contrib import admin
from django.core import management
from django.test import TestCase

from .apps import ControlledVocabularyConfig
from .models import (
    ControlledTerm,
    ControlledTermField,
    ControlledVocabulary,
    term_create_from_string,
)


class ControlledVocTestCase(TestCase):
    """
    python manage.py test controlled_vocabulary
    python manage.py test controlled_vocabulary.tests.ControlledVocTestCase.test_search_list_by_termid
    """

    @classmethod
    def setUpTestData(cls):
        # This is no longer necessary because:
        # a) voc files are downloaded on demand
        # b) voc records are updated each time the project starts
        # management.call_command("vocab", "init", verbosity=0)
        pass

    def test_vocab_init(self):
        '''Find built-in voc created by "vocab init"'''
        ControlledVocabulary.objects.get(prefix="mime")

    def test_try_all_vocabularies(self):
        """Make sure all default vocabularies return something"""
        cases = [
            ["iso15924", "hiero"],
            ["iso639-2", "art"],
            ["schema", "Movie"],
            ["dcmitype", "Image"],
            ["mime", "jpeg"],
            ["fast-topic", "Politics"],
            ["fast-forms", "criticism"],
            ["wikidata", "belgium"],
            ["viaf", "obama"],
        ]
        for case in cases:
            manager = ControlledVocabularyConfig.get_vocabulary_manager(case[0])
            self.assertIsNotNone(
                manager, "can't find manager for prefix '{}'".format(case[0])
            )
            terms = manager.search(case[1])
            self.assertTrue(
                len(terms) > 0,
                "Search for '{}' in '{}' didn't return anything".format(
                    case[1], case[0]
                ),
            )

    def test_term_create_from_code(self):
        """Create new term & voc from code"""
        for i in range(2):
            ControlledTerm.get_or_create_from_code("avoc:123:My Term")

            ControlledTerm.objects.get(
                vocabulary__prefix="avoc", termid="123", label="My Term"
            )

    def test_term_create_from_string(self):
        v = "1"
        term_id = "123"
        term_label = "le label"
        term_description = "a long description"

        value = None
        self.assertIsNone(term_create_from_string(value))

        value = "{}::{}::{}".format(v, term_id, term_label)
        term_pk = term_create_from_string(value)
        self.assertIsNotNone(term_pk)
        self.assertGreater(term_pk, 0)

        value = "{}::{}::{}::".format(v, term_id, term_label)
        term_pk = term_create_from_string(value)
        self.assertIsNotNone(term_pk)
        self.assertGreater(term_pk, 0)

        value = "{}::{}::{}::{}".format(v, "le-label", term_label, term_description)
        term_pk = term_create_from_string(value)
        self.assertIsNotNone(term_pk)
        self.assertGreater(term_pk, 0)

        term = ControlledTerm.objects.get(pk=term_pk)
        self.assertEqual(term_description, term.description)

    def test_search_lang_by_label(self):
        prefix = "iso639-2"

        manager = ControlledVocabularyConfig.get_vocabulary_manager(prefix)

        terms = manager.search("engl")
        # expect at least 'English', 'English, Middle', 'English, Old'
        self.assertGreater(len([t for t in terms if "English" in t[1]]), 2)
        self.assertEqual(terms[0][1], "English")

        terms = manager.search("german")
        # expect at least 'English', 'English, Middle', 'English, Old'
        self.assertGreater(len([t for t in terms if "German" in t[1]]), 2)
        self.assertEqual(terms[0][1], "German")
        self.assertEqual(terms[1][1], "German")
        self.assertNotEqual(terms[0][0], terms[1][0])

        terms = manager.search("german2")
        self.assertEqual(len(terms), 0)

    def test_search_lang_by_termid(self):
        """base_list.search() should lookup termid as well as label
        See gh-8
        """

        prefix = "iso639-2"
        termid = "glv"
        label = "Manx"

        # search by termid using the voc manager
        manager = ControlledVocabularyConfig.get_vocabulary_manager(prefix)

        terms = manager.search("glv")
        self.assertEqual(terms[0][1], "Manx")
        terms = manager.search("deu")
        self.assertEqual(terms[0][1], "German")

    def test_search_term_or_none(self):
        """search_term_or_none()"""
        prefix = "wikidata"
        pattern_exact = "pytest"
        pattern_partial = "pytes"

        from .utils import search_term_or_none

        if 1:
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

            self.assertNotEqual(
                "Essay", search_term_or_none("fast-topic", "Essay").label
            )
            self.assertEqual(
                "Essay", search_term_or_none("fast-topic", "Essay", exact=True).label
            )

        # make sure we don't have that termid in the database already
        prefix = "iso639-2"
        termid = "glv"
        label = "Manx"
        self.assertFalse(
            ControlledTerm.objects.filter(
                vocabulary__prefix=prefix, termid=termid
            ).exists()
        )

        term = search_term_or_none(prefix, termid)
        self.assertEqual(term.label, label)

        # make sure we have that termid in the database now
        self.assertTrue(
            ControlledTerm.objects.filter(
                vocabulary__prefix=prefix, termid=termid
            ).exists()
        )

        term = search_term_or_none(prefix, termid)
        self.assertEqual(term.label, label)

        term = search_term_or_none(prefix, label)
        self.assertEqual(term.termid, termid)

        # ---

        term = search_term_or_none(prefix, "English")
        self.assertEqual(term.termid, "eng")

        term = search_term_or_none(prefix, "french")
        self.assertEqual(term.termid, "fre")

        term = search_term_or_none(prefix, "fre")
        self.assertEqual(term.termid, "fre")
        term = search_term_or_none(prefix, "german")
        self.assertEqual(term.termid, "ger")

        term = search_term_or_none(prefix, "deu")
        self.assertEqual(term.termid, "deu")

    def test_iso15924(self):
        manager = ControlledVocabularyConfig.get_vocabulary_manager("iso15924")

        terms = manager.search("anatol")
        self.assertEqual(terms[0][0], "Hluw")
