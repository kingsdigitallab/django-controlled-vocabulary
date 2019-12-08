from django.conf import settings
import os

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

CONTROLLED_VOCABULARY_DATA_ROOT = os.path.join(
    settings.MEDIA_ROOT, 'vocabularies'
)


def get_var(name):
    '''
    Returns the value of a settings variable.
    The full name is CONTROLLED_VOCABULARY_ + name.
    First look into django settings.
    If not found there, use the value defined in this file.
    '''
    full_name = 'CONTROLLED_VOCABULARY_' + name
    ret = globals().get(full_name, None)
    ret = getattr(settings, full_name, ret)
    return ret
