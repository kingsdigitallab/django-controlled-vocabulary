# Django Controlled Vocabulary

Facilitates linkage to remote standard vocabularies (e.g. language codes, geonames) within the Django Admin to increase the consistency and understandability of your project data.

Development Status: Alpha (only partly functional, work in progress)

# Features

* Lets you create your own controlled lists of terms (i.e. **local** lists)
* [TODO] look up terms from **remote** vocabularies (i.e. authority lists)
* **plug-in architecture** for lookups into particular vocabularies:
  * Hard-coded lists: DCMI types
  * CSV
  * Python libraries
  * [TODO] Sparql: TGN
  * [TODO] Rest API
* Built-in vocabulary plug-ins:
  * ISO 639-2 (Language codes)
  * DCMI Type (Dublin Core resource types)
* **stores** used terms from remote vocabularies:
  * space efficient (don't clutter the database with unused terms)
  * self-contained (i.e. can still works offline & DB always 'semantically' complete)
* [TODO] possibility to store additional **metadata** (e.g. geonames coordinates)
* simple **rest API** to publish your own terms
* **autocomplete** input widget for django admin
  * [TODO] vocabulary selector

# Data Models
* ControlledVocabulary
  * label, prefix, base_url, description
* ControlledTerm:
  * label, termid, vocabulary (-> ControlledVocabulary)

# Limitations
* **controlled list** rather than fully fledged vocabularies, (i.e. just a bag of terms with unique IDs/URIs, no support for taxonomic relationships among terms like broader, narrower, synonyms, ...)
* no notion of granularity (e.g. geonames country, region, city, street are all treated as part of the same vocabulary)

# Setup

## Installation

Install into your environment:

```
pip install django-controlled-vocabulary
```

Add the app to the INSTALLED_APPS list in your Django settings file:

```
INSTALLED_APPS = [
    # other apps
    'controlled_vocabulary',
]
```

Run the migrations:

```
./manage.py migrate
```

## Configuration

### Enabling vocabulary plug-ins

A Vocabulary plug-in / manager is a python class that provide services for a vocabulary:
* implement the search() method used to dynamically look up terms in the admin interface
* supplies metadata for the vocabulary

Add the following code in your settings.py to enable vocabularies based on the import path of their classes.

```
# List of import paths to vocabularies lookup classes
# you can overwrite this in your django settings.py
CONTROLLED_VOCABULARY_VOCABULARIES = [
    'controlled_vocabulary.vocabularies.iso639_2',
    'controlled_vocabulary.vocabularies.dcmitype',
]
```

After enabling new vocabularies you'll need to run the following django command create or update records in the database for all enabled vocabulary plug-ins.

```
./manage.py vocab update
```

And this command to download the data files for the built-in vocabularies.

```
./manage.py vocab download
```

Note that this command only adds or update but never removes vocabularies from the database or changes terms.

## Usage

To define a controlled term in your Django Model, use the following field:

```
from controlled_vocabulary.models import ControlledTermField
```

```
    language_code = ControlledTermField(
        'iso639-2',
        null=True, blank=True
    )
```

Where 'iso639-2' is the prefix of a controlled vocabulary in your database.


