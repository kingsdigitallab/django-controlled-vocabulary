"""
Default static settings for the controlled_vocabulary app
All settings variables can be overridden in your django project settings.py

See controlled_vocabulary/settings.py for dynamic settings.
"""

# List of import paths to vocabularies lookup classes
CONTROLLED_VOCABULARY_VOCABULARIES = [
    "controlled_vocabulary.vocabularies.iso639_2",
    "controlled_vocabulary.vocabularies.dcmitype",
    "controlled_vocabulary.vocabularies.schema",
    "controlled_vocabulary.vocabularies.mime",
    "controlled_vocabulary.vocabularies.fast_topic",
    "controlled_vocabulary.vocabularies.fast_forms",
    "controlled_vocabulary.vocabularies.wikidata",
    "controlled_vocabulary.vocabularies.viaf",
    "controlled_vocabulary.vocabularies.iso15924",
]
