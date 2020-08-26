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
