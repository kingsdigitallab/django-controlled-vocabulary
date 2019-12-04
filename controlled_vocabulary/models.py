from django.db import models
from django.contrib.admin.widgets import AutocompleteSelect
from django.urls.base import reverse
from django import forms

LENGTH_LABEL = 200
LENGTH_IDENTIFIER = 50
# TODO: make that a config setting
LOCAL_VOCABULARY_BASE_URL = 'http://localhost:8000/vocabularies'


class ControlledVocabulary(models.Model):
    prefix = models.CharField(max_length=LENGTH_IDENTIFIER, unique=True)
    label = models.CharField(max_length=LENGTH_LABEL, unique=True)
    # TODO: rename namespace?
    base_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    concept = models.CharField(
        max_length=LENGTH_IDENTIFIER, null=False, blank=True, default='')

    class Meta:
        ordering = ['prefix']
        verbose_name_plural = 'Controlled vocabularies'

    def get_absolute_url(self):
        ret = (self.base_url or '').strip()

        if not ret:
            # local web path for local vocabulary
            ret = LOCAL_VOCABULARY_BASE_URL.rstrip('/')
            ret = '{}/{}'.format(ret, self.prefix)

        return ret

    def __str__(self):
        return self.label


class ControlledTerm(models.Model):
    vocabulary = models.ForeignKey(
        ControlledVocabulary,
        on_delete=models.CASCADE
    )
    termid = models.CharField(max_length=LENGTH_LABEL)
    label = models.CharField(max_length=LENGTH_LABEL)
    definition = models.TextField(null=True, blank=True)

    # We store json in this field.
    # Only Postgresql supports JSONField at this time.
    data = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['termid']
        unique_together = ['vocabulary', 'termid']

    def get_absolute_url(self):
        ret = self.vocabulary.get_absolute_url()
        if not ret.endswith('/'):
            ret += '/'
        ret += self.termid
        return ret

    def get_absolute_id(self):
        return '{}:{}'.format(self.vocabulary.prefix, self.termid)

    def __str__(self):
        return '{} ({})'.format(self.label, self.vocabulary.prefix)


class ControlledTermWidget(AutocompleteSelect):

    url_name = 'controlled_vocabulary_terms'

    def __init__(self, rel, admin_site, prefix, attrs=None, choices=(), using=None):
        self.prefix = prefix
        if attrs is None:
            attrs = {}
        attrs['data-voc-prefix'] = self.prefix
        super().__init__(rel, admin_site, attrs=attrs, choices=choices, using=using)

    def get_url(self):
        model = self.rel.model
        return reverse(self.url_name, kwargs={'prefix': self.prefix})

    @property
    def media(self):
        other = forms.Media(
            js=(
                # init.js is included here to ensure the order is correct
                # see Media.merge()
                'admin/js/jquery.init.js',
                'admin/js/controlled_term_widget.js',
                # repeated to make sure it is run after ours
                'admin/js/autocomplete.js',
            ),
            css={
                'screen': (
                    'admin/css/controlled_term_widget.css',
                ),
            },
        )
        return super().media + other

    def value_from_datadict(self, *args, **kwargs):
        ret = super().value_from_datadict(*args, **kwargs)
        if ret:
            parts = str(ret).split(':')
            if len(parts) == 3:
                # 10:abc
                # where 10 is a ControlledVocabulary.id
                # and abc is a ControlledTerm.termid
                # We return the ControlledTerm.id
                term, created = ControlledTerm.objects.get_or_create(
                    vocabulary_id=parts[0],
                    termid=parts[1],
                    label=parts[2]
                )
                ret = term.id
        return ret


class ControlledTermField(models.ForeignKey):
    def __init__(self, vocabularies, to='controlled_vocabulary.ControlledTerm', on_delete=models.SET_NULL, related_name='+', *args, **kwargs):
        '''
        vocabularies: a list of vocabularies the user can chose terms from.
            The first entry of the list is the default vocabulary.
            An entry has one of the following format:
                prefix, e.g. 'iso639-2'
                *concept, e.g. '*Language'
                '', any vocabulary
            Example: ['iso639-2', '*language', '']
            'iso639-2' is the default voc on page load, but the user can
            also change to all vocabularies that have the concept = language,
            or any other vocabulary.

            vocabularies='myvoc' is syntactic sugar for ['myvoc']
        '''

        self.vocabularies = vocabularies

        super().__init__(to, on_delete, related_name, *args, **kwargs)

    def formfield(self, *args, **kwargs):
        '''We use a different widget than the base class'''
        from django.contrib import admin
        kwargs['widget'] = ControlledTermWidget(
            self.remote_field, admin.site, self.vocabularies)
        return super().formfield(*args, **kwargs)
