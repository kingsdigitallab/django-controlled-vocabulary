from .base_list import VocabularyBase
import json


class VocabularyWikidata(VocabularyBase):
    prefix = 'wikidata'
    label = 'Wikidata'
    base_url = 'http://www.wikidata.org/entity/'
    concept = 'wikidata:Q35120:entity'
    description = 'TODO'
    source = {
        'url': 'https://www.wikidata.org/w/api.php?action=wbsearchentities&language=en&format=json&search={pattern}',
    }

    def search(self, pattern):
        ret = []
        if len(pattern) < 3:
            return ret
        url = self.source['url'].format(pattern=pattern)

        from .base import fetch
        content = fetch(url)

        content = content.decode('utf8')

        res = json.loads(content)
        for hit in res['search']:
            ret.append([hit['id'], hit['label'], hit.get('description', '')])

        return ret
