def api_data_processor(data, user_type, user_limit=0):
    """**Preprocesa los datos de elasticsearch para la api**

    Recibe la respuesta de elasticsearch en crudo y organiza los datos
    para dar una respuesta más ordenada dependiendo del tipo de
    usuario.

    :param data: Respuesta en crudo de elasticsearch
    :type: dict
    :param user_type: Tipo de usuario que hacer la peticion a la api
    :type: str
    :param user_limit: Limite de resultados a mostrar en la api
    :type: int
    :return: Diccionario con los datos organizados para la respuesta de la api
    :rtype: dict
    """
    data_set = []
    result = {}
    hits = data["hits"] if not user_limit else data["hits"][:user_limit]
    for hit in hits:
        fields = hit.keys()
        result["document_name"] = hit["_source"]["document_name"]
        result["pdf_file"] = hit["_source"]["pdf_file"]
        if "variant" in hit["_source"].keys() and user_type != "anon":
            result["variant"] = hit['_source']['variant']
        else:
            if user_type != "anon":
                result["variant"] = ""
        if "highlight" in fields and user_type != "anon":
            result["highlight"] = hit["highlight"]
        else:
            if user_type != "anon":
                result["highlight"] = ""
        result["l1"] = hit["_source"]["l1"]
        result["l2"] = hit["_source"]["l2"]
        data_set.append(result)
        result = {}
    return data_set


def get_source_ip(request):
    """**Función encargada de obtener la IP del cliente**

    Se obtiene la IP para poder verificar los límites para usuarios
    anonimos que hagan consultas a la API

    :param request: Objeto ``HttpRequets`` para pasar el estado de la app a
                    través del sistema
    :type: ``HttpRequest``
    :return: IP que hace la petición a la API
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
