# django-controlled-vocabulary
Link your data to authority lists or your own controlled lists

# Features

* create your own terms (local control lists)
* [TODO] look up terms from remote vocabularies
* plug-in architecture for lookups and particular vocabularies:
  * Python libraries: Language codes
  * Hard-coded lists: DCMI types
  * [TODO] Sparql: TGN
  * [TODO] Rest API
  * CSV
* store used terms from remote vocs:
  * space efficient
  * self-contained (i.e. can still works offline & DB remains complete)
* [TODO] possibility to store additional metadata (e.g. geonames coordinates)
* simple rest API to publish terms (could even use that as a remote source, i.e. connect our datasets)
* autocomplete input widget for django admin
  * [TODO] vocabulary selector

# Data Models
* ControlledVocabulary
  * label, prefix, base_url, description
* ControlledTerm:
  * label, termid, vocabulary (-> ControlledVocabulary)

# Limitations
* **controlled list** rather than fully fledged vocabularies, (i.e. just a bag of terms with unique IDs/URIs, no support for taxonomic relationships among terms like broader, narrower, synonyms, ...)
* no notion of granularity (e.g. geonames country, region, city, street are all treated as part of the same vocabulary)

