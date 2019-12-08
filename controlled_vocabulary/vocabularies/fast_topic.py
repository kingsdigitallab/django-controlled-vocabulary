from .base import VocabularyBase
import json
import re


class VocabularyFastTopic(VocabularyBase):
    # https://www.oclc.org/developer/develop/web-services/fast-api/linked-data.en.html
    # TODO: not sure what the recommended prefix is?
    prefix = 'fast-topic'
    label = 'FAST Topic'
    base_url = 'http://id.worldcat.org/fast/'
    concept = 'wikidata:P921:topic'
    description = 'Topic list from the Faceted Application of Subject Terminology'
    # also downloadable but 50MB+ for RDF file.
    source = {
        # 'url': 'http://fast.oclc.org/searchfast/fastsuggest?query={query}&fl=suggest50&rows=10',
        'url': 'https://fast.oclc.org/searchfast/fastsuggest?&query={query}&queryIndex=suggest50&queryReturn=suggest50,id&sort=usage desc&suggest=fastSuggest',
        # https://www.oclc.org/research/themes/data-science/fast/download.html
        # 'url': 'https://researchworks.oclc.org/researchdata/fast/FASTTopical.nt.zip',
    }

    def _get_clean_id(self, fastid):
        # fst00809209_4.1 => 809209
        ret = fastid
        matches = re.findall(r'[1-9][0-9]+', ret)
        if matches:
            ret = matches[0]
        return ret

    def search(self, pattern):
        ret = []
        if len(pattern) < 2:
            return ret
        url = self.source['url'].format(query=pattern)

        from .base import fetch
        content = fetch(url)

        content = content.decode('utf8')

        res = json.loads(content)
        for doc in res['response']['docs']:
            ret.append([self._get_clean_id(doc['id']), doc['suggest50']])

        return ret
