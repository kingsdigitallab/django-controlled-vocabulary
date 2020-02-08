from .models import ControlledVocabulary, ControlledTerm
from .apps import ControlledVocabularyConfig


def search_term_or_none(prefix: str, pattern: str, exact=False) -> 'ControlledTerm':
    '''Returns a `ControlledTerm` for the `ControlledVocabulary` with the
    given `prefix` and `pattern`.

    It searches in the external vocabulary and returns the first matching term
    If exact is True it will return None if the exact pattern is not found.
    It also saves the term in the database if it doesn't already exists.

    Returns None if no vocabulary with that prefix is found.
    Returns None if the pattern is None or empty.
    '''
    ret = None

    if prefix and pattern:
        try:
            ret = search_term(prefix, pattern, exact=exact)
        except ControlledVocabulary.DoesNotExist:
            pass

    return ret


def search_term(prefix: str, pattern: str, exact=False) -> 'ControlledTerm':
    """Returns a `ControlledTerm` for the `ControlledVocabulary` with the
    given `prefix` and `pattern`.

    It first searches for an exact match in the DB (ControlledTerm).
    It then searches in the external vocabulary
        and returns the first matching term.
    If exact is True it will return None if the first found term is not an
        exact match of pattern.
    It also saves the term in the database if it doesn't already exists.

    Throws an exception if no vocabulary with that prefix is found.
    """

    ret = None

    # try the DB first
    from django.db.models import Q

    ret = ControlledTerm.objects.filter(
        Q(termid__iexact=pattern) | Q(label__iexact=pattern),
        vocabulary__prefix=prefix
    ).first()
    if ret:
        return ret

    # external search
    cv = ControlledVocabulary.objects.get(prefix=prefix)
    manager = ControlledVocabularyConfig.get_vocabulary_manager(cv.prefix)

    terms = manager.search(pattern)

    if terms:
        term = terms[0]

        if (not exact
            or (term[1].lower() == pattern.lower())
                or (term[0].lower() == pattern.lower())):
            desc = term[2] if len(term) > 2 else ''
            ret, _ = ControlledTerm.objects.get_or_create(
                vocabulary=cv, termid=term[0].strip(),
                defaults={'label': term[1], 'description': desc}
            )

    return ret
