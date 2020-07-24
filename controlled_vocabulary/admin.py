from django.contrib import admin
from .models import ControlledVocabulary, ControlledTerm
from django.utils.safestring import mark_safe


class TermInline(admin.TabularInline):
    fields = ["termid", "label"]
    model = ControlledTerm
    max_num = 100
    extra = 5


@admin.register(ControlledVocabulary)
class ControlledVocabularyAdmin(admin.ModelAdmin):
    list_display = ["label", "concept", "is_managed"]
    list_display_links = ["label"]
    inlines = [TermInline]

    def is_managed(self, obj):
        ret = ""

        from .apps import ControlledVocabularyConfig

        voc_manager = ControlledVocabularyConfig.get_vocabulary_manager(obj.prefix)

        if voc_manager:
            ret = "managed"

        return ret


@admin.register(ControlledTerm)
class ControlledTermAdmin(admin.ModelAdmin):
    list_display = ["termid", "label", "vocabulary"]
    search_fields = ["termid", "label"]
    list_filter = ["vocabulary"]
    readonly_fields = ["admin_field_uri", "admin_field_absolute_id"]

    fields = [
        "vocabulary",
        "termid",
        "label",
        "description",
        "admin_field_uri",
        "admin_field_absolute_id",
    ]

    def admin_field_uri(self, obj):
        return mark_safe('<a href="{0}">{0}</a>'.format(obj.uri))

    admin_field_uri.short_description = "URI"

    def admin_field_absolute_id(self, obj):
        return obj.get_absolute_id()

    admin_field_absolute_id.short_description = "absolute id"
