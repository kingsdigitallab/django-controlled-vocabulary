from .base_list import VocabularyBaseList


class VocabularyDCMIType(VocabularyBaseList):
    prefix = 'dcmitype'
    label = 'DCMI Type'
    base_url = 'http://purl.org/dc/dcmitype/'
    concept = 'Type of resource'
    description = 'a general, cross-domain list of approved terms ' + \
        'that may be used as values for the Dublin Core Resource Type ' +\
        'element to identify the genre of a resource'

    def _get_searchable_terms(self):
        ret = [
            ['Collection', 'Collection'],
            ['Dataset', 'Dataset'],
            ['Event', 'Event'],
            ['Image', 'Image'],
            ['InteractiveResource', 'Interactive Resource'],
            ['MovingImage', 'Moving Image'],
            ['PhysicalObject', 'Physical Object'],
            ['Service', 'Service'],
            ['Software', 'Software'],
            ['Sound', 'Sound'],
            ['StillImage', 'Still Image'],
            ['Text', 'Text'],
        ]
        return ret
