from .base_csv import VocabularyBaseCSV
import json


class VocabularyFastTopic(VocabularyBaseCSV):
    # https://www.oclc.org/developer/develop/web-services/fast-api/linked-data.en.html
    # TODO: not sure what the recommended prefix is?
    prefix = 'fast-topic'
    label = 'FAST Topic'
    base_url = 'http://id.worldcat.org/fast/{identifier}/{format}'
    concept = 'wikidata:P921:topic'
    description = 'Topic list from the Faceted Application of Subject Terminology'
    # also downloadable but 600MB+ for RDF file.
    source = {
        # 'url': 'http://fast.oclc.org/searchfast/fastsuggest?query={query}&fl=suggest50&rows=10',
        'url': '',
    }

    def search(self, pattern):
        ret = []
        if len(pattern) < 3:
            return ret
        url = self.source['url'].format(query=pattern)

        from .base import fetch
        content = fetch(url)

        content = content.decode('utf8')

        res = json.loads(content)
        for doc in res['response']['docs']:
            ret.append(doc['suggest50'], doc['suggest50'])

        return ret
