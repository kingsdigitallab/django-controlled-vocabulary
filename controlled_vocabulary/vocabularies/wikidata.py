from .base_http import VocabularyHTTP
import json


class VocabularyWikidata(VocabularyHTTP):
    prefix = "wikidata"
    label = "Wikidata"
    base_url = "http://www.wikidata.org/entity/"
    concept = "wikidata:Q35120:entity"
    description = "TODO"
    source = {
        "url": "https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search={pattern}",
    }

    def parse_search_response(self, res):
        ret = []

        for hit in res["search"]:
            ret.append([hit["id"], hit["label"], hit.get("description", "")])

        return ret
