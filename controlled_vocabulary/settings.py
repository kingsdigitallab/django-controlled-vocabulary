from django.conf import settings
import os

'''
Default settings for the controlled_vocabulary app
All settings variables can be overridden in your django project settings.py
'''

# List of import paths to vocabularies lookup classes
CONTROLLED_VOCABULARY_VOCABULARIES = [
    'controlled_vocabulary.vocabularies.iso639_2',
    'controlled_vocabulary.vocabularies.dcmitype',
    'controlled_vocabulary.vocabularies.schema',
    'controlled_vocabulary.vocabularies.mime',
    'controlled_vocabulary.vocabularies.fast_topic',
    'controlled_vocabulary.vocabularies.fast_forms',
    'controlled_vocabulary.vocabularies.wikidata',
    'controlled_vocabulary.vocabularies.viaf',
]

# The absolute path to the folder where vocabulary files will be downloaded
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
