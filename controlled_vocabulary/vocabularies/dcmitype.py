from .base_list import VocabularyBaseList


class VocabularyDCMIType(VocabularyBaseList):
    prefix = "dcmitype"
    label = "DCMI Type"
    base_url = "http://purl.org/dc/dcmitype/"
    concept = "wikidata:Q5165081:content format"
    description = (
        "a general, cross-domain list of approved terms "
        + "that may be used as values for the Dublin Core Resource Type "
        + "element to identify the genre of a resource"
    )

    # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#dcmitype-Collection
    def _get_searchable_terms(self):
        ret = [
            ["Collection", "Collection", "An aggregation of resources"],
            [
                "Dataset",
                "Dataset",
                "Data encoded in a defined structure (e.g. list, table, database).",
            ],
            ["Event", "Event"],
            ["Image", "Image"],
            ["InteractiveResource", "Interactive Resource"],
            ["MovingImage", "Moving Image"],
            ["PhysicalObject", "Physical Object"],
            [
                "Service",
                "Service",
                "A system that provides one or more functions (e.g. interlibrary loans, banking service, web server).",
            ],
            ["Software", "Software"],
            ["Sound", "Sound"],
            ["StillImage", "Still Image"],
            ["Text", "Text"],
        ]
        return ret
