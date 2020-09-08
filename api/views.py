import logging
import elasticsearch
from .helpers import api_data_processor
from searcher.helpers import variant_to_query, get_variants, query_kreator
from django.conf import settings
from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import (api_view, permission_classes,
                                       authentication_classes,
                                       throttle_classes)
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from api.throttles import (SustainedRateAnonThrottle, BurstRateAnonThrottle,
                          SustainedRateUserThrottle, BurstRateUserThrottle)
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as es_exceptions

LOGGER = logging.getLogger(__name__)

# Cliente de `elasticsearch`
es = Elasticsearch([settings.ELASTIC_URL])

@api_view(['GET'])
def info(request):
    """Endpoint con información disponible de la API"""
    current_variants = get_variants()
    del current_variants["status"]
    return Response({"variants": current_variants, "l1": settings.L1,
                     "l2": settings.L2})


@api_view(['POST'])
@throttle_classes([BurstRateAnonThrottle, SustainedRateAnonThrottle])
def basic_search(request):
    """Endpoint para busquedas básicas de la API"""
    anon_limit = 10
    if request.method == "POST":
        variants = ""
        data = request.data
        lang = data["lang"]
        query = query_kreator(f"{lang}:{data['query']}{variants}")
        r = es.search(index=settings.INDEX, body=query, scroll="1m")
        data_response = r["hits"]
        total_entries = data_response["total"]["value"]
        preprocess_data = api_data_processor(data_response, anon_limit)
        return Response({"query": data["query"],
                         "results": preprocess_data,
                         "total_results": total_entries})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([BurstRateUserThrottle, SustainedRateUserThrottle])
def full_search(request):
    if request.method == "POST":
        entries = 0
        user_limit = 100
        data = request.data
        lang = data["lang"]
        variants = ""
        if "variants" in data.keys() and data["variant"]:
            variants = " AND variant:" + variant_to_query(data["variants"])
        query = query_kreator(f"{lang}:{data['query']}{variants}")
        r = es.search(index=settings.INDEX, body=query, scroll="1m")
        data_response = r["hits"]
        scroll_id = r["_scroll_id"]
        total_entries = data_response["total"]["value"]
        entries_count = len(data_response["hits"])
        while entries_count != total_entries and entries_count <= user_limit :
            sub_response = es.scroll(scroll_id=scroll_id, scroll="1m")
            data_response["hits"] += sub_response["hits"]["hits"]
            entries_count += len(sub_response["hits"]["hits"])
            scroll_id = sub_response["_scroll_id"]
        preprocess_data = api_data_processor(data_response, limit=user_limit)
        return Response({"query": data["query"],
                         "results": preprocess_data,
                         "total_results": total_entries})
