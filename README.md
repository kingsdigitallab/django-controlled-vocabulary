# Django Controlled Vocabulary

Facilitates linkage to remote standard vocabularies (e.g. language codes, geonames) within the Django Admin to increase the consistency and understandability of your project data.

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

TODO

## Configuration

TODO

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


