import fnmatch

from .base import VocabularyBase, chrono
from .base_list import VocabularyBaseList
from ..settings import get_var
import os
import re


class VocabularyBaseCSV(VocabularyBaseList):
    """
    Abstract manager that can search from a CSV File.
    The subclass just needs to override _get_terms_from_csv_line()
    and the class properties describing the vocabulary and the source.
    """

    label = "Abstract CSV Vocabulary"
    base_url = ""
    # subclass should override source
    source = {
        "url": "http://id.loc.gov/vocabulary/iso639-2.tsv",
        # optional, delimiter
        # if unspecified the delimiter is a comma
        "delimiter": "\t",
        # optional, whether the file is missing a headers row
        "missing_header": False,
        # optional, name of downloaded file
        # If unspecified, the filename is derived from the end of the url
        "filename": "language-639-2.tsv",
        # optional, the path of a file to extract from the downloaded url
        "extract": "file_to_extract",
    }

    def _get_terms_from_csv_line(self, line):
        '''Subclass should override this method.
        line: an list of values from a csv row
        return a list of terms, each term has the form:
            [termid, label]
            [termid, label, description]
        '''
        # example: returns one term where termid = first cell, label = second
        return [[line[0], line[1]]]
        raise Exception('This function should be overridden')

    def _get_data_root(self):
        ret = get_var("DATA_ROOT")
        return ret

    def _get_searchable_terms(self):
        """Returns all terms from the CSV.
        Download the CSV if it doesn't exist yet.
        """
        ret = []
        import csv

        filepath = self._get_filepath()

        if not os.path.exists(filepath):
            download_info = self.download()
            if download_info[2] < 1:
                raise Exception("download {} failed".format(filepath))

        options = {}
        if "delimiter" in self.source:
            options["delimiter"] = self.source["delimiter"]

        with open(filepath) as tsv:
            first_line = not self.source.get("missing_header", False)
            for line in csv.reader(tsv, **options):
                if not first_line and len(line) > 1:
                    for term in self._get_terms_from_csv_line(line):
                        if term is not None:
                            ret.append(term)
                first_line = False

        return ret

    def download(self, overwrite=False):
        """Download self.source"""
        from .base import fetch

        url = self.source["url"]
        filepath = self._get_filepath()
        size = 0
        downloaded = 0

        if re.search("^https?://", url):
            if overwrite or not os.path.exists(filepath):
                content = fetch(url)

                if content is not None:
                    size = len(content)
                    downloaded = 1

                    input_path = self._get_filepath(True)
                    with open(input_path, "wb") as fh:
                        fh.write(content)

                    filepath = self._process_file(input_path)
            else:
                size = os.path.getsize(filepath)

        return [url, filepath, size, downloaded]

    def _process_file(self, input_path):
        '''optionally transform the downloaded file
        or extract something from it.'''
        ret = input_path
        ret = self._extract_file(ret)
        ret = self._rename_file(ret)

        return ret

    def _extract_file(self, input_path):
        '''extract a file from an archive.
        Currently supported: .zip
        '''
        ret = input_path

        extract_pattern = self.source.get('extract', None)
        if extract_pattern:
            ret = None
            if input_path.endswith('.zip'):
                import zipfile
                with zipfile.ZipFile(input_path, 'r') as zh:
                    for info in zh.infolist():
                        if fnmatch.fnmatch(info.filename, extract_pattern):
                            ret = zh.extract(info, self._get_data_root())
                            break
            else:
                raise Exception(
                    'Type of vocabulary archive not supported {}'.format(
                        input_path
                    )
                )

        if ret is None:
            raise Exception('"{}" not found in archive {}'.format(
                extract_pattern, input_path
            ))

        return ret

    def _rename_file(self, input_path):
        '''rename input_path into source['processed']
        '''
        ret = input_path
        processed = self.source.get('processed', None)
        if processed:
            ret = self._get_absolute_path(processed)
            os.rename(input_path, ret)

        return ret

    def _get_filepath(self, unprocessed=False):
        '''returns the path to the file that contains the terms.
        If unprocessed is False: returns the path to the processed file
            (i.e. a CSV)
        Otherwise, returns the path to the 'raw' downloaded file.
            If there is no processing, it will be the same as unprocessed=False
        '''
        ret = None
        if not unprocessed:
            ret = self.source.get('processed', None)

        if not ret:
            ret = os.path.basename(self.source["url"])

        return self._get_absolute_path(ret)

    def _get_absolute_path(self, relative_path):
        return os.path.join(self._get_data_root(), relative_path)

