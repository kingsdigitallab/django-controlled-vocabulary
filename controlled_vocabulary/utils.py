import re
from typing import Optional

from .apps import ControlledVocabularyConfig
from .models import ControlledTerm, ControlledVocabulary


def search_term(
    prefix: str, pattern: str, exact: bool = False
) -> Optional["ControlledTerm"]:
    """Returns a `ControlledTerm` for the `ControlledVocabulary` with the
    given `prefix` and `pattern`.

    'pattern' is a plain string, not a regular expression.

    Method:
        first searches for an exact match in the DB (ControlledTerm).
        It then searches using the external vocabulary / voc manager
        and returns the first matching term.
        If that secondary search is successful, it will save found term
        in the database as new ControlledTerm record.

    If 'exact' is True it only consider an exact match on the label or termid.
    Otherwise, it returns the first term which label or termid contains the
    given pattern.

    Returns None if no match is found.

    Throws an exception if no vocabulary with that prefix is found.
    """

    # try the DB first
    from django.db.models import Q

    ret = ControlledTerm.objects.filter(
        Q(termid__iexact=pattern) | Q(label__iexact=pattern), vocabulary__prefix=prefix
    ).first()
    if ret:
        return ret

    # search using the voc manager
    vocabulary = ControlledVocabulary.objects.get(prefix=prefix)
    manager = ControlledVocabularyConfig.get_vocabulary_manager(
        vocabulary.prefix
    )

    pattern = pattern.lower()
    terms = manager.search(pattern)

    if terms:
        term = None

        for t in terms:
            if exact:
                if t[1].lower() == pattern or t[0].lower() == pattern:
                    term = t
                    break
            else:
                if pattern in t[1].lower() or pattern in t[0].lower():
                    term = t
                    break

        if term:
            desc = term[2] if len(term) > 2 else ""
            ret, _ = ControlledTerm.objects.get_or_create(
                vocabulary=vocabulary,
                termid=term[0].strip(),
                defaults={"label": term[1], "description": desc},
            )

    return ret


def search_term_or_none(
    prefix: str, pattern: str, exact: bool = False
) -> Optional["ControlledTerm"]:
    """Returns a `ControlledTerm` for the `ControlledVocabulary` with the
    given `prefix` and `pattern`.

    Behaves like search_term() except that it will return None
    if the vocabulary prefix doesn't exist.
    """
    ret = None

    if prefix and pattern:
        try:
            ret = search_term(prefix, pattern, exact=exact)
        except ControlledVocabulary.DoesNotExist:
            pass

    return ret


