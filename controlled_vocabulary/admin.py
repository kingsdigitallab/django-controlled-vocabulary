from django.contrib import admin
from .models import ControlledVocabulary, ControlledTerm


class TermInline(admin.TabularInline):
    fields = ['termid', 'label']
    model = ControlledTerm
    max_num = 100
    extra = 5


@admin.register(ControlledVocabulary)
class ControlledVocabularyAdmin(admin.ModelAdmin):
    list_display = ['label', 'concept', 'is_managed']
    list_display_links = ['label']
    inlines = [TermInline]

    def is_managed(self, obj):
        ret = ''

        from .apps import ControlledVocabularyConfig
        voc_manager = ControlledVocabularyConfig.get_vocabulary_manager(
            obj.prefix
        )

        if voc_manager:
            ret = 'managed'

        return ret


@admin.register(ControlledTerm)
class ControlledTermAdmin(admin.ModelAdmin):
    list_display = ['termid', 'label', 'vocabulary']
    search_fields = ['termid', 'label']
    list_filter = ['vocabulary']
