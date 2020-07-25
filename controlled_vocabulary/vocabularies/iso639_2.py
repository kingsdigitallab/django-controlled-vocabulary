from .base_csv import VocabularyBaseCSV


class VocabularyISO639_2(VocabularyBaseCSV):
    """https://www.loc.gov/standards/iso639-2/faq.html
    http://lists.xml.org/archives/xml-dev/200108/msg00758.html
    e.g. french: fre (B), fra (T); german: ger (B), deu (T)
    """
    prefix = "iso639-2"
    label = "ISO 639-2"
    base_url = "http://id.loc.gov/vocabulary/iso639-2/"
    concept = "wikidata:Q34770:language"
    description = (
        "Codes for the Representation of Names of Languages"
        " - Part 2: Alpha-3 Code for the Names of Languages"
    )
    # we no longer use this source as it doesn't distinguish b/w T & B
    # source = {
    #     "url": "http://id.loc.gov/vocabulary/iso639-2.tsv",
    #     "delimiter": "\t",
    # }
    source = {
        "url": "https://www.loc.gov/standards/iso639-2/ISO-639-2_utf-8.txt",
        "delimiter": "|",
        "missing_header": True,
    }

    def _get_terms_from_csv_line(self, line):
        # arm|hye|hy|Armenian|arménien
        ret = [[line[0], line[3]]]

        if line[1].strip():
            ret.append([line[1], line[3]])
            ret[0].append('B')
            ret[1].append('T')

        return ret
