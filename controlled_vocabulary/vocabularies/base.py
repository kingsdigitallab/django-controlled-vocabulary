
class VocabularyBase():
    prefix = 'base'
    label = 'Abstract Vocabulary'
    base_url = ''
    description = ''
    concept = ''


def fetch(url):
    import urllib3
    # TODO: error management
    headers = {'user-agent': 'django-controlled-vocabulary/0.1'}
    http = urllib3.PoolManager(headers=headers)
    request = http.request('GET', url)
    return request.data
