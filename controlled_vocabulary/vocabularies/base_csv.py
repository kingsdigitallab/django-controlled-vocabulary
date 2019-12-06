from .base_list import VocabularyBaseList
import os
import re


class VocabularyBaseCSV(VocabularyBaseList):
    '''
    Abstract manager that can search from a predefined list.
    The subclass just needs to override _get_term_from_csv_line()
    '''
    label = 'Abstract Vocabulary'
    base_url = ''
    # subclass should override source
    source = {
        'url': 'http://id.loc.gov/vocabulary/iso639-2.tsv',
        'delimiter': '\t',
    }

    # subclass should override this method
    def _get_term_from_csv_line(self, line):
        return [line[1], line[1]]

    def _get_filepath(self):
        ret = os.path.join(
            os.path.dirname(__file__),
            os.path.basename(self.source['url'])
        )

        return ret

    def _get_searchable_terms(self):
        ret = []
        import csv

        filepath = self._get_filepath()

        if not os.path.exists(filepath):
            raise Exception('{} not found'.format(filepath))

        options = {}
        if 'delimiter' in self.source:
            options['delimiter'] = self.source['delimiter']

        with open(filepath) as tsv:
            first_line = True
            for line in csv.reader(tsv, **options):
                if not first_line and len(line) > 2:
                    term = self._get_term_from_csv_line(line)
                    if term is not None:
                        ret.append(term)
                first_line = False

        return ret

    def download(self):
        '''Download self.source'''
        from .base import fetch

        url = self.source['url']
        filepath = self._get_filepath()
        if re.search('^https?://', url):
            content = fetch(url)

            size = len(content)

            with open(filepath, 'wb') as fh:
                fh.write(content)
        else:
            size = 0

        return [url, filepath, size]
