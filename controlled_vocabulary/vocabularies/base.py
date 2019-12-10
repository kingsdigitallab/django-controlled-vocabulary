
class VocabularyBase():
    '''Abstract vocabulary management / plugin class.
    Subclasses MUST override the following fields.
    '''
    # The standard prefix for this vocabulary, see http://prefix.cc
    prefix = 'base'
    # A short label for the vocabulary
    label = 'Abstract Vocabulary'
    # The base URL for all terms in this vocabulary, see http://prefix.cc
    base_url = ''
    # A sentence or paragraph describing this vocabulary
    description = ''
    # A wikidata term that best characterise the terms in this vocabulary
    # e.g. 'wikidata:Q34770:language'
    concept = ''


def chrono(msg):
    from datetime import datetime
    now = datetime.now()
    now_str = now.strftime("%d-%b-%Y (%H:%M:%S.%f)")
    print(now_str, msg)
