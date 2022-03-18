import re

from .base_http import VocabularyHTTP


class VocabularyFastTopic(VocabularyHTTP):
    # https://www.oclc.org/developer/develop/web-services/fast-api/linked-data.en.html
    # TODO: not sure what the recommended prefix is?
    prefix = "fast-topic"
    label = "FAST Topic"
    base_url = "http://id.worldcat.org/fast/"
    concept = "wikidata:P921:topic"
    description = "Topic list from the Faceted Application of Subject Terminology"
    source = {
        # 'url': 'http://fast.oclc.org/searchfast/fastsuggest?query={query}&fl=suggest50&rows=10',
        "url": "https://fast.oclc.org/searchfast/fastsuggest?&query={pattern}&queryIndex=suggest50&queryReturn=suggest50,id&sort=usage desc&suggest=fastSuggest&rows=20",
        # https://www.oclc.org/research/themes/data-science/fast/download.html
        # 'url': 'https://researchworks.oclc.org/researchdata/fast/FASTTopical.nt.zip',
    }

    def _get_clean_id(self, fastid):
        # fst00809209_4.1 => 809209
        ret = fastid
        matches = re.findall(r"[1-9][0-9]+", ret)
        if matches:
            ret = matches[0]
        return ret

    def parse_search_response(self, res):
        ret = []

        for doc in res["response"]["docs"]:
            ret.append([self._get_clean_id(doc["id"]), doc["suggest50"]])
        return ret
