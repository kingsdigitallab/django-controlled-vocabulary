import urllib.parse

from django.http import JsonResponse
from django.http.response import Http404
from django.shortcuts import render
from django.views.generic.list import ListView

from .models import ControlledTerm, ControlledVocabulary


class TermListView(ListView):
    model = ControlledTerm
    paginate_by = 10

    def _get_vocabulary_record_from_request(self):
        """Returns the requested vocabulary prefix (from url)"""
        prefix = self.request.GET.get("prefix") or self.kwargs.get("prefix")
        ret = ControlledVocabulary.objects.filter(prefix=prefix).first()
        return ret

    def _get_query_from_request(self):
        """returns the value of the q parameter in the query string"""
        return self.request.GET.get("term", "")

    def get_queryset(self):
        voc_record = self._get_vocabulary_record_from_request()
        if not voc_record:
            raise Http404()

        # get the manager for this voc
        from .apps import ControlledVocabularyConfig

        voc_manager = ControlledVocabularyConfig.get_vocabulary_manager(
            voc_record.prefix
        )

        # if no voc, we do a DB query
        user_query = self._get_query_from_request()
        if not (voc_manager):
            return self.model.objects.filter(
                vocabulary=voc_record, label__icontains=user_query
            )

        # search with manager
        # TODO: use a generator,
        # wasteful to convert all entries to ControlledTerm()
        # if only few displayed
        ret = []
        for term in voc_manager.search(user_query):
            description = ""
            if len(term) > 2:
                description = term[2]
            term = ControlledTerm(
                termid=term[0],
                label=term[1],
                vocabulary=voc_record,
                description=description,
            )
            ret.append(term)

        return ret

    def render_to_response(self, context, **response_kwargs):
        page_obj = context["page_obj"]
        # this format conforms with select2 / django autocomplete API
        res = {
            "results": [
                {
                    "id": term.pk
                    or "{}::{}::{}::{}".format(
                        term.vocabulary_id,
                        term.termid,
                        term.label,
                        urllib.parse.quote_plus(term.description),
                    ),
                    "termid": term.termid,
                    "text": term.label,
                    "description": term.description,
                }
                for term in page_obj
            ],
            "pagination": {"more": page_obj.has_next()},
        }
        return JsonResponse(res)
