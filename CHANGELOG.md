# Changelog

## 0.8 (26-07-2020)

* Tried to reduce the need for running `vocab init`:
    * a) remote voc files (like CSVs) are now automatically downloaded on demand.
    E.g. utils.search_term('iso639-2', 'eng'') would trigger a download of 
    the CSV if it's not on disk already. This is the same as `vocab fetch`.
    * b) each time the project is launched (e.g. ./manage.py XXX) the voc app
    will insert/update the ControlledVocabulary records from the metadata 
    provided by the enabled vocabulary managers (i.e. same as `vocab update`).
    * c) the same will also happen at the end of the second migration 0002_X
* This should hopefully solve the issues with initial set up/migration of a project
or data migrations that need to call utils.search_term().   
* . See [issue #9](https://github.com/kingsdigitallab/django-controlled-vocabulary/issues/9)

## 0.7 (24-07-2020)

* WARNING: breaking change - renamed _get_term_from_csv_line() into 
_get_terms_from_csv_line() (in base_csv.py and subclasses). The output
is now a list of terms rather than a single term. This is because some
vocabulary file may contain more than one term on a single CSV line (e.g. iso369-2).
* added a new action to the vocab command line tool. `vocab search -f iso639-2 -p engl` 
will do a term lookup directly on the given vocabulary manager (i.e. it bypasses
utils.search_term()) and display the array of matching terms. It's very useful
for testing and debugging. Unlike the widgets or utils.search_term(), it won't
use the database at all (no read, no write). The results and their order should 
be identical to those returned by the widget
* improved the treatment of ambiguous terms in iso639-2. E.g. fra vs fre 
or deu vs ger. See the github issue for more details
* improved the matching and sorting of terms in base_list.py search() and
in utils.search_term(). Documentation should be more accurate
* fixed a bug in base_list.py search() where only one exact match would be 
returned
* See [issue 10](https://github.com/kingsdigitallab/django-controlled-vocabulary/issues/10)
and
[issue 8](https://github.com/kingsdigitallab/django-controlled-vocabulary/issues/8)
