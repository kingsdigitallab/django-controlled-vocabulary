import os

from .defaults import *  # noqa

from django.conf import settings

"""
Default dynamic settings for the controlled_vocabulary app
All settings variables can be overridden in your django project settings.py

See controlled_vocabulary/defaults.py for static settings.
"""

# The absolute path to the folder where vocabulary files will be downloaded
CONTROLLED_VOCABULARY_DATA_ROOT = os.path.join(settings.MEDIA_ROOT, "vocabularies")


def get_var(name):
    """
    Returns the value of a settings variable.
    The full name is CONTROLLED_VOCABULARY_ + name.
    First look into django settings.
    If not found there, use the value defined in this file.
    """
    full_name = "CONTROLLED_VOCABULARY_" + name
    ret = globals().get(full_name, None)
    ret = getattr(settings, full_name, ret)
    return ret
