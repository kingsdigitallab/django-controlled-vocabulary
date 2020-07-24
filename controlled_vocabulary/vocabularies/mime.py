from .base_csv import VocabularyBaseCSV
import re


class VocabularyMime(VocabularyBaseCSV):
    prefix = "mime"
    label = "Media Types"
    base_url = "https://www.iana.org/assignments/media-types/"
    # File format
    concept = "wikidata:Q235557:file format"
    description = "web page topics indexable by web search engines"
    source = {
        "url": "https://pkgstore.datahub.io/core/media-types/media-types_csv/data/923aafab3de13cee5844f9329222c5c5/media-types_csv.csv",
    }

    def _get_terms_from_csv_line(self, line):
        return [[line[0], line[0]]]
