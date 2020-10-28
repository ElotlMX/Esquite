import logging
import elasticsearch
from searcher.helpers import variant_to_query, query_kreator
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
from .helpers import api_data_processor, get_source_ip

LOGGER = logging.getLogger(__name__)

# Cliente de `elasticsearch`
es = Elasticsearch([settings.ELASTIC_URL])


@api_view(['POST'])
@throttle_classes([BurstRateAnonThrottle, SustainedRateAnonThrottle])
def basic_search(request):
    """Endpoint para búsquedas básicas de la API

    Se pueden realizar búsquedas que devolverán una cantidad limitada de
    resultados. No es posible buscar por variante y los resultados omiten
    el *highlight* automático. Tambien la cantidad de request por hora y
    día será muy limitada.
    """
    anon_limit = settings.API['limit_results']['anon']
    ip_client = get_source_ip(request)
    client_type = "anon"
    fields = ["lang", "query", "index"]
    if request.method == "POST":
        data = request.data
        if set(fields) - set(data.keys()) != set():
            missing_fields = set(fields).difference(set(data.keys()))
            return Response(
                {
                    "detail": "Missing fields in JSON request",
                    "missing_fields": missing_fields,
                    "error": "bad_request"
                }, status=status.HTTP_400_BAD_REQUEST)
        lang = data["lang"]
        LOGGER.info(f"lang:{lang}::query:{data['query']}::{ip_client}::{client_type}")
        query = query_kreator(f"{lang}:{data['query']}")
        try:
            r = es.search(index=data["index"], body=query, scroll="1m")
            data_response = r["hits"]
            total_entries = data_response["total"]["value"]
            preprocess_data = api_data_processor(data_response, client_type,
                                                 user_limit=anon_limit)
            response = {"query": data["query"],
                        "index": data["index"],
                        "total_results": total_entries,
                        "showed_results": anon_limit,
                        "results": preprocess_data,
                       }
            status_code = status.HTTP_200_OK
        except elasticsearch.exceptions.RequestError as e:
            info = e.info['error']['root_cause'][0]
            string_code = "status:" + str(e.status_code)
            error_type = f"type:{info['type']}"
            reason = f"reason:{info['reason']}"
            index = f"index:{info['index']}"
            LOGGER.error("::".join([error_type, reason, string_code, index,
                                    ip_client, client_type]))
            response = {"error": error_type,
                        "detail": "No se pudo concretar la búsqueda :("}
            status_code = e.status_code
        except elasticsearch.exceptions.ConnectionError as e:
            error_type = "conection-timeout"
            index_name = f"index:{data['index']}"
            url = f"url:{settings.URL}"
            LOGGER.error("::".join([error_type, index_name, url, ip_client,
                                   client_type]))
            response = {"error": error_type,
                        "detail": "No se pudo conectar con el server :("}
            status_code = e.status_code
        except elasticsearch.exceptions.NotFoundError as e:
            info = e.info['error']['root_cause'][0]
            index = f"index:{data['index']}"
            status_code = "status:" + str(e.status_code)
            error_type = f"type:{info['type']}"
            reason = f"reason:{info['reason']}"
            error_type = "index_not_found"
            LOGGER.error("::".join([error_type, index, ip_client,
                                   client_type]))
            response = {"error": error_type,
                        "detail": "No se encontró el índice de elasticsearch :("}
            status_code = e.status_code
        return Response(response, status=status_code)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@throttle_classes([BurstRateUserThrottle, SustainedRateUserThrottle])
def full_search(request):
    """Endpoint para búsquedas completas de la API

    Se pueden realizar búsquedas añadiendo el campo de variante a la query.
    El limite de resultados es mayor al de las búsquedas básicas y los
    resultados incluyen el campo de *highlight* automático. La cantidad de
    request por hora y día será más amplia que en las búsquedas básicas.
    """
    user_limit = settings.API['limit_results']['user']
    ip_client = get_source_ip(request)
    client_type = "user"
    fields = ["lang", "query", "index", "variants"]
    if request.method == "POST":
        entries = 0
        variants = ""
        data = request.data
        if set(fields) - set(data.keys()) != set():
            # Getting missing fields with set operation
            missing_fields = set(fields) - (set(data.keys()))
            return Response(
                {
                    "detail": "Missing fields in JSON request",
                    "missing_fields": missing_fields,
                    "error": "bad_request"
                }, status=status.HTTP_400_BAD_REQUEST)
        if data["variants"]:
            variants = " AND variant:" + variant_to_query(data["variants"])
        lang = data["lang"]
        # TODO: Create get_logger_msg()
        LOGGER.info(f"lang:{lang}::query:{data['query']}::{ip_client}::{client_type}")
        query = query_kreator(f"{lang}:{data['query']}{variants}")
        try:
            r = es.search(index=data['index'], body=query, scroll="1m")
            data_response = r["hits"]
            scroll_id = r["_scroll_id"]
            total_entries = data_response["total"]["value"]
            entries_count = len(data_response["hits"])
            # Scroll over the index to get all entries
            while entries_count != total_entries and entries_count <= user_limit:
                sub_response = es.scroll(scroll_id=scroll_id, scroll="1m")
                data_response["hits"] += sub_response["hits"]["hits"]
                entries_count += len(sub_response["hits"]["hits"])
                scroll_id = sub_response["_scroll_id"]
            preprocess_data = api_data_processor(data_response, client_type,
                                                 user_limit=user_limit)
            response = {"query": data["query"],
                        "index": data["index"],
                        "total_results": total_entries,
                        "showed_results": user_limit,
                        "results": preprocess_data,
                       }
            status_code = status.HTTP_200_OK
        except elasticsearch.exceptions.RequestError as e:
            info = e.info['error']['root_cause'][0]
            status_code = "status:" + str(e.status_code)
            error_type = f"type:{info['type']}"
            reason = f"reason:{info['reason']}"
            index = f"index:{info['index']}"
            LOGGER.error("::".join([error_type, reason, status_code, index,
                                    ip_client, client_type]))
            response = {"error": error_type,
                        "detail": "No se pudo concretar la búsqueda :("}
            status_code = e.status_code
        except elasticsearch.exceptions.ConnectionError as e:
            error_type = "conection-timeout"
            index_name = f"index:{settings.INDEX}"
            url = f"url:{settings.URL}"
            LOGGER.error("::".join([error_type, index_name, url, ip_client,
                                   client_type]))
            response = {"error": error_type,
                        "detail": "No se pudo conectar con el server :("}
            status_code = e.status_code
        except elasticsearch.exceptions.NotFoundError as e:
            info = e.info['error']['root_cause'][0]
            index = f"index:{data['index']}"
            status_code = "status:" + str(e.status_code)
            error_type = f"type:{info['type']}"
            reason = f"reason:{info['reason']}"
            error_type = "index_not_found"
            LOGGER.error("::".join([error_type, index, ip_client,
                                   client_type]))
            response = {"error": error_type,
                        "detail": "No se encontró el índice de elasticsearch :("}
            status_code = e.status_code
        return Response(response, status=status_code)
