from .base import VocabularyBase


class VocabularyBaseList(VocabularyBase):
    """
    Abstract manager that can search from a predefined list.
    The subclass just needs to override _get_searchable_terms()
    """

    label = "Abstract Vocabulary"
    base_url = ""

    def _get_searchable_terms(self):
        """
        Subclass needs to override this function.
        """
        ret = (
            ("en", "English"),
            ("fr", "French"),
        )
        return ret

    def search(self, pattern):
        """Returns terms that match the given patterns
        among those found in the full list supplied by _get_searchable_terms.

        Matching rules:
            comparisons are case-insensitive
            match any term which label contains <pattern>
            match any term which termid matches exactly with <pattern>

        Sorting priorities (highest first):
            exact match on the termid and label
            exact match on the termid [4]
            exact match on the label [1]
            beginning of label matches the pattern (then alphabetical) [1]
            any part of the label matches the pattern (then alphabetical) [1]
        """
        # get all terms from the subclass and cache them in the object
        self._searchable_terms = getattr(self, "_searchable_terms", None)
        if self._searchable_terms is None:
            # leave this here, so we only lazy-load terms
            # the first time they are needed.
            self._searchable_terms = self._get_searchable_terms()

            # sort alphabetically
            self._searchable_terms = sorted(self._searchable_terms, key=lambda t: t[1])

        ret = []

        # return only terms that match the input pattern
        pattern = pattern.lower()

        if pattern:
            for term in self._searchable_terms:
                score = 0
                label = term[1].lower()
                tid = term[0].lower()
                if pattern in label: score += 1
                if term[0].lower() == pattern: score += 4
                if score:
                    if label.startswith(pattern): score += 1
                    if label == pattern: score += 1
                    desc = ''
                    if len(term) > 2:
                        desc = term[2]
                    ret.append([term[0], term[1], desc, score])

            # sort by score, then label then description
            ret = sorted(ret, key=lambda t: [-t[3], t[1], t[2]])
        else:
            # returns everything
            ret = self._searchable_terms

        return ret
