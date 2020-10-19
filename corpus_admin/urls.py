from django.urls import path
from . import views

urlpatterns = [
    path('', views.list_docs, name='list-docs'),
    path('new/', views.new_doc, name='new-doc'),
    path('preview/<str:_id>', views.doc_preview, name="preview"),
    path('edit/<str:_id>', views.doc_edit, name='edit'),
    path('add/<str:_id>', views.add_doc_data, name='add'),
    path('delete/', views.delete_doc, name='delete'),
    path('export-corpus-data/', views.export_data, name="export-corpus-data"),
    path('index-config/', views.index_config, name="index-config")
]
