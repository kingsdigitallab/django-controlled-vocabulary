# Django Controlled Vocabulary
Link your data to authority lists or your own controlled lists

# Features

* lets you create your own terms (**local** control lists)
* [TODO] look up terms from **remote** vocabularies (i.e. authority lists)
* **plug-in architecture** for lookups into particular vocabularies:
  * Python libraries: Language codes
  * Hard-coded lists: DCMI types
  * [TODO] Sparql: TGN
  * [TODO] Rest API
  * CSV
* Built-in vocabulary plug-ins:
  * ISO 639-2 (Language codes)
  * DCMI Type (Dublin Core resource types)
* **stores** used terms from remote vocabularies:
  * space efficient (don't clutter the database with unused terms)
  * self-contained (i.e. can still works offline & DB always 'semantically' complete)
* [TODO] possibility to store additional **metadata** (e.g. geonames coordinates)
* simple **rest API** to publish terms (could even use that as a remote source, i.e. connect our datasets)
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

