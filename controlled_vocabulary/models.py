import urllib.parse

from django import forms
from django.contrib.admin.widgets import AutocompleteSelect, AutocompleteSelectMultiple
from django.db import models
from django.forms.widgets import SelectMultiple
from django.urls.base import reverse

LENGTH_LABEL = 200
LENGTH_IDENTIFIER = 50
# TODO: make that a config setting
LOCAL_VOCABULARY_BASE_URL = "http://localhost:8000/vocabularies"


class ControlledTerm(models.Model):
    vocabulary = models.ForeignKey("ControlledVocabulary", on_delete=models.CASCADE)
    termid = models.CharField(max_length=LENGTH_LABEL)
    label = models.CharField(max_length=LENGTH_LABEL)
    description = models.TextField(null=True, blank=True)

    # We store json in this field.
    # Only Postgresql supports JSONField at this time.
    data = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["termid"]
        unique_together = ["vocabulary", "termid"]
        verbose_name = "Controlled Term"

    def get_absolute_url(self):
        ret = self.vocabulary.get_absolute_url()
        if not ret.endswith("/"):
            ret += "/"
        ret += self.termid
        return ret

    @property
    def uri(self):
        return self.get_absolute_url()

    def get_absolute_id(self):
        return "{}:{}".format(self.vocabulary.prefix_base, self.termid)

    @classmethod
    def get_or_create_from_code(cls, code):
        """code has the following format: prefix:termid:label.
        Creates vocabulary record if needed.
        """
        return cls._get_or_create_from_code(code, ControlledVocabulary, ControlledTerm)

    @staticmethod
    def _get_or_create_from_code(code, vocabulary_model, term_model):
        """
        'vocabulary_model' can be either
        <class 'controlled_vocabulary.models.ControlledVocabulary'>
        or <class '__fake__.ControlledVocabulary'>

        same with term_model.
        """
        ret = None

        parts = code.split(":")
        if len(parts) == 3:
            voc, _ = vocabulary_model.objects.get_or_create(
                prefix=parts[0].lower().strip()
            )
            ret, _ = term_model.objects.get_or_create(
                vocabulary=voc, termid=parts[1].strip(), defaults={"label": parts[2]}
            )

        return ret

    def __str__(self):
        return "{} ({})".format(self.label, self.vocabulary.prefix)


class ControlledTermWidgetMixin:
    url_name = "controlled_terms"
    template_name = "controlled_vocabulary/controlled_term.html"

    def __init__(
        self, rel, admin_site, vocabularies, attrs=None, choices=(), using=None
    ):
        if isinstance(vocabularies, str):
            self.vocabularies = [vocabularies, ""]
        else:
            self.vocabularies = vocabularies
        super().__init__(rel, admin_site, attrs=attrs, choices=choices, using=using)

    def get_url(self):
        return reverse(self.url_name)

    def get_context(self, name, value, attrs):
        from django.db.models import Q

        context = super().get_context(name, value, attrs)

        context["vocabularies"] = ControlledVocabulary.objects.all()

        if "" not in self.vocabularies:
            # filter vocabularies based on their prefix or concept
            # e,g, ['iso-639-2', 'concept.wikidata:Q35120']
            context["vocabularies"] = context["vocabularies"].filter(
                Q(
                    prefix__in=[
                        voc for voc in self.vocabularies if "concept." not in voc
                    ]
                )
                | Q(
                    concept__termid__in=[
                        voc.split(":")[-1]
                        for voc in self.vocabularies
                        if "concept." in voc
                    ]
                )
            )

        default_voc = context["vocabularies"][0]
        for voc in context["vocabularies"]:
            if voc.prefix == self.vocabularies[0]:
                default_voc = voc
                break

        prefix = default_voc.prefix
        context["default_prefix"] = prefix
        context["widget"]["attrs"]["data-voc-prefix"] = prefix

        return context

    @property
    def media(self):
        ret = super().media
        ret += forms.Media(
            js=(
                # init.js is included here to ensure the order is correct
                # see Media.merge()
                "admin/js/jquery.init.js",
                "admin/js/controlled_term_widget.js",
                # repeated to make sure it is run after ours
                "admin/js/autocomplete.js",
            ),
            css={
                "screen": ("admin/css/controlled_term_widget.css",),
            },
        )
        return ret

    def value_from_datadict(self, *args, **kwargs):
        """
        Called when the user saves a parent record.
        It transforms the widget value into the id of a Term record.
        We have to create the Term record on the fly as its value
        comes from an autocomplete service.

        termid:label:description
        """
        ret = super().value_from_datadict(*args, **kwargs)

        return self._value_from_datadict(ret)

    def _value_from_datadict(self, value):
        return self._value_from_datadict_single(value)

    def _value_from_datadict_single(self, value):
        return term_create_from_string(value)


def term_create_from_string(value):
    """Get or create a term from a string value. The string must follow the format:
    vocabulary_id::term_id::term_label::term_description. The term_description is
    optional."""
    if not value:
        return None

    parts = str(value).split("::")
    if len(parts) < 3:
        return value

    desc = None
    if len(parts) == 4:
        desc = urllib.parse.unquote_plus(parts[3])

    term, created = ControlledTerm.objects.get_or_create(
        vocabulary_id=parts[0],
        termid=parts[1],
        defaults={"label": parts[2], "description": desc},
    )

    return term.id


class ControlledTermWidget(ControlledTermWidgetMixin, AutocompleteSelect):
    pass


class ControlledTermsWidget(ControlledTermWidgetMixin, AutocompleteSelectMultiple):
    def _value_from_datadict(self, value):

        ret = value

        if isinstance(ret, list):
            ret = [self._value_from_datadict_single(val) for val in ret]

        return ret


class ControlledTermField(models.ForeignKey):
    def __init__(
        self,
        vocabularies,
        to="controlled_vocabulary.ControlledTerm",
        on_delete=models.SET_NULL,
        related_name="+",
        *args,
        **kwargs
    ):
        """
        vocabularies: a list of vocabularies the user can chose terms from.
            The first entry of the list is the default vocabulary.
            An entry has one of the following format:
                'iso639-2': a vocabulary prefix
                'concept.Language': vocabulary concept
                '': any vocabulary
            Example: ['iso639-2', 'concept.language', '']
            'iso639-2' is the default voc on page load, but the user can
            also change to all vocabularies that have the concept = language,
            or any other vocabulary.

            vocabularies='myvoc' is syntactic sugar for ['myvoc']
        """

        self.vocabularies = vocabularies

        super().__init__(to, on_delete, related_name, *args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["vocabularies"] = self.vocabularies
        return name, path, args, kwargs

    def formfield(self, *args, **kwargs):
        """We use a different widget than the base class"""
        from django.contrib import admin

        kwargs["widget"] = ControlledTermWidget(
            self.remote_field, admin.site, self.vocabularies
        )
        return super().formfield(*args, **kwargs)


class ControlledTermsField(models.ManyToManyField):
    def __init__(
        self,
        vocabularies,
        to="controlled_vocabulary.ControlledTerm",
        related_name="+",
        *args,
        **kwargs
    ):
        """vocabularies: see ControlledTermField"""

        self.vocabularies = vocabularies

        super().__init__(to, related_name, *args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        kwargs["vocabularies"] = self.vocabularies
        return name, path, args, kwargs

    def formfield(self, *args, **kwargs):
        """We use a different widget than the base class"""
        from django.contrib import admin

        kwargs["widget"] = ControlledTermsWidget(
            self.remote_field, admin.site, self.vocabularies
        )
        return super().formfield(*args, **kwargs)


class ControlledVocabulary(models.Model):
    prefix = models.CharField(max_length=LENGTH_IDENTIFIER, unique=True)
    label = models.CharField(max_length=LENGTH_LABEL, unique=True)
    base_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    concept = ControlledTermField("wikidata", null=True, blank=True)

    class Meta:
        ordering = ["prefix"]
        verbose_name = "Controlled Vocabulary"
        verbose_name_plural = "Controlled Vocabularies"

    def get_absolute_url(self):
        ret = (self.base_url or "").strip()

        if not ret:
            # local web path for local vocabulary
            ret = LOCAL_VOCABULARY_BASE_URL.rstrip("/")
            ret = "{}/{}".format(ret, self.prefix)

        return ret

    @property
    def prefix_base(self):
        return self.prefix.split("/")[0]

    def __str__(self):
        return self.label
