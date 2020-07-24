from .base_csv import VocabularyBaseCSV
import re


def decamel(keyword):
    return re.sub(r"([A-Z])", r" \1", keyword).strip()


class VocabularySchema(VocabularyBaseCSV):
    prefix = "schema"
    label = "Schema.org"
    base_url = "http://schema.org/"
    concept = "wikidata:Q35120:entity"
    description = "web page topics indexable by web search engines"
    # https://schema.org/docs/developers.html#defs
    source = {
        "url": "https://schema.org/version/latest/schema-types.csv",
    }

    def _get_terms_from_csv_line(self, line):
        return [[line[1], decamel(line[1])]]
