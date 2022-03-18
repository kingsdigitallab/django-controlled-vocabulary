from .base_csv import VocabularyBaseCSV


class VocabularyISO15924(VocabularyBaseCSV):
    """https://www.unicode.org/iso15924/codelists.html
    """
    # TODO: TBC
    prefix = "iso15924"
    label = "ISO 15924"
    # TODO: TBC, not dereferenceable
    base_url = "https://www.unicode.org/iso15924/"
    concept = "wikidata:Q8192:writing system"
    description = "Codes for the Representation of names of scripts"
    source = {
        "url": "https://www.unicode.org/iso15924/iso15924.txt",
        "processed": "iso15924-utf8.txt",
        'delimiter': ';',
    }

    def _get_terms_from_csv_line(self, line):
        ret = []
        if not line[0].startswith('#'):
            ret = [[line[0], line[2]]]

        return ret
