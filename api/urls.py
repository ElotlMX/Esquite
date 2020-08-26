from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('', views.info, name='api-info'),
    path('search/', views.basic_search, name='basic_search'),
    path('full-search/', views.full_search, name='full_search'),
    path('api-token-auth/', obtain_auth_token, name='api_token_auth'),
]
