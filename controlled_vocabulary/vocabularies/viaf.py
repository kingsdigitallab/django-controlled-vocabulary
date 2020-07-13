from .base_http import VocabularyHTTP


class VocabularyViaf(VocabularyHTTP):
    # https://platform.worldcat.org/api-explorer/apis/VIAF
    prefix = "viaf"
    label = "VIAF"
    base_url = "http://viaf.org/viaf/"
    concept = "wikidata:Q35120:entity"
    # http://viaf.org/viaf/data/
    description = (
        "VIAF (Virtual International Authority File) is an OCLC service"
        + " -- built in cooperation with national libraries and other partners"
        + " -- that virtually combines multiple LAM (Library Archives"
        + " Museum) name authority files into a single name authority service."
    )
    source = {
        # Issue with autosuggest is that it won't always return what you want:
        # e.g. http://www.viaf.org/viaf/AutoSuggest?query=london
        "url": "http://www.viaf.org/viaf/AutoSuggest?query={pattern}"
    }

    def parse_search_response(self, res):
        ret = []

        if "result" in res and res["result"] is not None:
            for doc in res["result"]:
                ret.append([doc["viafid"], doc["term"]])

        return ret
