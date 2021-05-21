from modeltranslation.translator import translator, TranslationOptions
from controlled_vocabulary.models import ControlledTerm

class ControlledTermOptions(TranslationOptions):
    fields = ('label', 'description')

translator.register(ControlledTerm, ControlledTermOptions)
