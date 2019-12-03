from django.urls import path

from . import views

urlpatterns = [
    path(
        '<slug:prefix>/terms/',
        views.TermListView.as_view(),
        name='controlled_vocabulary_terms'
    ),
]
