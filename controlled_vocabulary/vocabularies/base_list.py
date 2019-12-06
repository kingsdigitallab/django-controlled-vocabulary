from .base import VocabularyBase


class VocabularyBaseList(VocabularyBase):
    '''
    Abstract manager that can search from a predefined list.
    The subclass just needs to override _get_searchable_terms()
    '''
    label = 'Abstract Vocabulary'
    base_url = ''

    def _get_searchable_terms(self):
        '''
        Subclass needs to override this function.
        '''
        ret = [
            ['en', 'English'],
            ['fr', 'French'],
        ]
        return ret

    def search(self, pattern):
        # get all terms from the subclass
        self._searchable_terms = getattr(self, '_searchable_terms', None)
        if self._searchable_terms is None:
            self._searchable_terms = self._get_searchable_terms()

            # sort alphabetically
            self._searchable_terms = sorted(
                self._searchable_terms, key=lambda t: t[1]
            )

        ret = []

        # return only terms that match the pattern
        pattern = pattern.lower()

        if pattern:
            exact_match = None
            start_match_count = 0
            for term in self._searchable_terms:
                if pattern in term[1].lower():
                    if term[1].lower() == pattern:
                        exact_match = term
                    elif term[1].lower().startswith(pattern):
                        ret.insert(start_match_count, term)
                        start_match_count += 1
                    else:
                        ret.append(term)
            if exact_match:
                ret.insert(0, exact_match)
        else:
            ret = self._searchable_terms

        return ret
