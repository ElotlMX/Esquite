from django.contrib import admin
from django.urls import path, include, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('links/', views.links, name='links'),
    path('about/', views.about, name='about'),
    path('participantes/', views.participants, name='participantes'),
    path('media/<path:file_name>', views.pdf_view, name="pdf_view"),
    path('admin/', admin.site.urls),
    path('search/', include('searcher.urls')),
    path('corpus-admin/', include('corpus_admin.urls')),
    path('v1/', include('api.urls')),
    re_path('^djga/', include('google_analytics.urls')),
]
