from .base import VocabularyBase, chrono
from .base_list import VocabularyBaseList
from ..settings import get_var
import os
import re


class VocabularyBaseCSV(VocabularyBaseList):
    """
    Abstract manager that can search from a predefined list.
    The subclass just needs to override _get_terms_from_csv_line()
    """

    label = "Abstract Vocabulary"
    base_url = ""
    # subclass should override source
    source = {
        "url": "http://id.loc.gov/vocabulary/iso639-2.tsv",
        "delimiter": "\t",
        "missing_header": False,
    }

    # subclass should override this method
    def _get_terms_from_csv_line(self, line):
        return [[line[1], line[1]]]

    def _get_data_root(self):
        ret = get_var("DATA_ROOT")
        return ret

    def _get_download_filepath(self, transformed=False):
        filename = os.path.basename(self.source["url"])

        if transformed and hasattr(self, "transform_download"):
            filename += ".trans.csv"

        ret = os.path.join(self._get_data_root(), filename)

        return ret

    def _get_searchable_terms(self):
        """Returns all terms from the CSV.
        Download the CSV if it doesn't exist yet.
        """
        ret = []
        import csv

        filepath = self._get_download_filepath(True)

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
        filepath = self._get_download_filepath()
        size = 0
        downloaded = 0

        if re.search("^https?://", url):
            if overwrite or not os.path.exists(filepath):
                content = fetch(url)

                if content is not None:
                    size = len(content)
                    downloaded = 1

                    with open(filepath, "wb") as fh:
                        fh.write(content)

                    transformer = getattr(self, "transform_download", None)
                    if transformer:
                        transformer()

            else:
                size = os.path.getsize(filepath)

        return [url, filepath, size, downloaded]
