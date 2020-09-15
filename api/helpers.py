def api_data_processor(data, limit=0):
    data_set = []
    result = {}
    hits = data["hits"] if not limit else data["hits"][:limit]
    for hit in hits:
        fields = hit.keys()
        result["document_name"] = hit["_source"]["document_name"]
        result["pdf_file"] = hit["_source"]["pdf_file"]
        if "variant" in hit["_source"].keys():
            result["variant"] = hit['_source']['variant']
        else:
            result["variant"] = ""
        if "highlight" in fields:
            result["highlight"] = hit["highlight"]
        result["l1"] = hit["_source"]["l1"]
        result["l2"] = hit["_source"]["l2"]
        data_set.append(result)
        result = {}
    return data_set


def get_source_ip(request):
    """Función encargada de obtener la IP del cliente

    Se obtiene la IP para poder verificar los límites para usuarios
    anonimos que hagan consultas a la API
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
