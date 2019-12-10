from .base import VocabularyBase
import json


def fetch_http(url):
    import urllib3
    # TODO: error management
    headers = {'user-agent': 'django-controlled-vocabulary/0.1'}
    http = urllib3.PoolManager(headers=headers)
    request = http.request('GET', url)
    return request.data


class VocabularyHTTP(VocabularyBase):
    '''Search with a http request.
    The subclass just needs to override parse_search_response().
    Supports only json responses at the moment.
    '''
    label = 'Abstract Vocabulary'
    base_url = ''
    source = {
        'url': 'https://some-domain.org/search/?&query={pattern}',
        'minimum_length': 1,
    }

    def parse_search_response(self, res):
        '''TO BE OVERRIDEN
        res: the http response as a python dictionary
        '''
        ret = []
        for doc in res['response']['docs']:
            ret.append([self._get_clean_id(doc['id']), doc['suggest50']])

        return ret

    def search(self, pattern):
        ret = []
        if len(pattern) < self.source.get('minimum_length', 1):
            return ret
        url = self.source['url'].format(pattern=pattern)

        content = fetch_http(url)
        content = content.decode('utf8')
        res = json.loads(content)

        ret = self.parse_search_response(res)

        return ret
