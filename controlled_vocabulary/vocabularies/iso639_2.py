from .base_csv import VocabularyBaseCSV


class VocabularyISO639_2(VocabularyBaseCSV):
    prefix = 'iso639-2'
    label = 'ISO 639-2'
    base_url = 'http://id.loc.gov/vocabulary/iso639-2/'
    concept = 'wikidata:Q34770:language'
    description = 'Codes for the Representation of Names of Languages'\
        ' - Part 2: Alpha-3 Code for the Names of Languages'
    source = {
        'url': 'http://id.loc.gov/vocabulary/iso639-2.tsv',
        'delimiter': '\t',
    }

    def _get_term_from_csv_line(self, line):
        return [line[1], line[2]]
