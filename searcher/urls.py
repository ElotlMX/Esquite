from django.urls import path
from . import views

urlpatterns = [
    path('', views.search, name='search'),
    path('ethnologue/<str:iso_variant>', views.ethnologue_data,
         name='ethnologue')
]
