def api_data_processor(data):
    data_set = []
    result = {}
    for hit in data["hits"]:
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
