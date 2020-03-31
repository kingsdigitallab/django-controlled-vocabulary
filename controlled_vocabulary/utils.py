import re
from typing import Optional

from .apps import ControlledVocabularyConfig
from .models import ControlledTerm, ControlledVocabulary


def search_term_or_none(
    prefix: str, pattern: str, exact: bool = False
) -> Optional["ControlledTerm"]:
    """Returns a `ControlledTerm` for the `ControlledVocabulary` with the
    given `prefix` and `pattern`.

    It searches in the external vocabulary and returns the first matching term
    If exact is True it will return None if the exact pattern is not found.
    It also saves the term in the database if it doesn't already exists.

    Returns None if no vocabulary with that prefix is found.
    Returns None if the pattern is None or empty.
    """
    ret = None

    if prefix and pattern:
        try:
            ret = search_term(prefix, pattern, exact=exact)
        except ControlledVocabulary.DoesNotExist:
            pass

    return ret


def search_term(
    prefix: str, pattern: str, exact: bool = False
) -> Optional["ControlledTerm"]:
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

    pattern = pattern.lower()
    terms = manager.search(pattern)

    if not terms:
        return None

    regex = re.compile(r"^" + pattern)

    term = terms[0]

    for t in terms:
        if exact:
            if t[1].lower() == pattern or t[0].lower() == pattern:
                term = t
                break
        else:
            if regex.match(t[1].lower()) or regex.match(t[0].lower()):
                term = t
                break

    if not term:
        return None

    desc = term[2] if len(term) > 2 else ""
    ret, _ = ControlledTerm.objects.get_or_create(
        vocabulary=cv,
        termid=term[0].strip(),
        defaults={"label": term[1], "description": desc},
    )

    return ret
