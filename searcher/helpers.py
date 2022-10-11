import csv
import logging

from django.conf import settings
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as es_exceptions

LOGGER = logging.getLogger(__name__)

# Cliente de `elasticsearch`
es = Elasticsearch([settings.ELASTIC_URL])


def highlighter(hit, idioma, query):
    """**Resalta la búsqueda realizada por el usuarix**

    Función que busca el campo ``highlight`` en los objetos devueltos por
    el API de ``elasticsearch`` y lo utilza para reemplazar el texto del
    idioma en el que se realizó la búsqueda. Si la búsqueda es en
    español, el texto dentro del campo highlight estará preprocesado por
    Elasticsearch.

    :param hit: Resultado de búsqueda
    :type: list
    :param idioma: ISO del idioma de búsqueda
    :type: str
    :param query: Cadena de búsqueda
    :type: str
    :return: Texto de los resultados resaltado
    :rtype: list
    """
    if "highlight" in hit:
        for key in hit['highlight'].keys():
            hit['_source'][key] = hit['highlight'][key].pop()
    elif idioma == "l2" and "highlight" not in hit:
        string = hit['_source']['l2']
        # Resaltado manual la lengua 2
        hit['_source']['l2'] = string.replace(query, '<em>' + query + "</em>")
    return hit


def data_processor(raw_data, idioma, query):
    """**Procesa los datos crudo de la API de Elasticsearh para devolver
    solo los resultados**

    Función que recibe una lista con los datos que prove la API de
    ``elacticsearch``, procesa los datos para ignorar los metadatos del API
    y retorna solo los resultados de búsqueda como una lista.

    :param raw_data: Lista de resultados crudos del API de Elasticsearch
    :type: list
    :param idioma: ISO del idioma de búsqueda
    :type: str
    :param query: Cadena de búsqueda
    :type: str
    :return: Resultados de búsqueda
    :rtype: list
    """
    # TODO: Refactor
    LOGGER.info("Procesando datos de Elasticsearch")
    data = []
    for hit in raw_data['hits']:
        fields = hit["_source"].keys()
        if "l1" not in fields and "l2" not in fields:
            hit["_source"]["l1"] = ''
            hit["_source"]["l2"] = ''
        elif "l1" not in fields:
            hit["_source"]["l1"] = ''
        elif "l2" not in fields:
            hit["_source"]["l2"] = ''
        hit = highlighter(hit, idioma, query)
        doc_name = hit['_source']['document_name']
        doc_file = hit['_source']['pdf_file']
        try:
            variant = hit['_source']['variant']
        except KeyError:
            variant = ""
        link = doc_file_to_link(doc_name, doc_file, settings.MEDIA_ROOT)
        if idioma == "NONE":
            # TODO: Este procesamiento es del preview del documento
            edit_btn = """<a href="#" class="btn btn-outline-info btn-block btn-sm disabled">Editar <i class="fa fa-edit"></i></a>"""
            delete_btn = """<a href="#" class="btn btn-outline-danger btn-block btn-sm disabled">Eliminar <i class="fa fa-close"></i></a>"""
            hit['_source']['actions'] = edit_btn + delete_btn
            hit['_source']['pdf_file'] = link
        else:
            hit['_source']['document_name'] = link
            if variant:
                hit['_source']['variant'] = ethno_btn_maker(variant)
        data.append(hit['_source'])
    return data


def query_kreator(term):
    """Crea la estructura para busquedas en Elasticsearch

    Función encargada de devolver el objeto con los elementos
    necesarios para realizar una búsqueda en Elasticsearch.
    Esto beneficia la limpieza del código reemplazando una variable
    estática

    :param term: Consulta introducida por la usuaria desde el Frontend
    :type: str
    """
    # TODO: Refinar la estructura para busquedas
    return {
        "version": True,
        "size": 10000,  # TODO: Variar para obetener mejor desempeño
        "sort": [{"_score": {"order": "desc"}}],
        "_source": {"excludes": []},
        "stored_fields": ["*"],
        "script_fields": {},
        "docvalue_fields": [],
        "query": {
            "bool": {
              "must": [
                {
                  "query_string": {
                    "query": term,
                    "analyze_wildcard": True
                  }
                }
              ],
              "filter": [],
              "should": [],
              "must_not": []
            }
        },
        "highlight": {
            "pre_tags": [
              "<em>"
            ],
            "post_tags": [
              "</em>"
            ],
            "fields": {
              "*": {}
            },
            "fragment_size": 2147483647
        }
    }


def doc_file_to_link(doc_name, doc_file, path):
    """**Función que liga el nombre de un documento con su archivo pdf**

    :param doc_name: Nombre del documento
    :type: str
    :param doc_file: Nombre del archivo
    :type: str
    :param path: Path donde se encuentran los pdfs
    :type: str
    :return: Nombre del documento con la liga al pdf
    :rtype: str
    """
    return f'<a href="{path + doc_file}" target="_blank">{doc_name}</a>'


def variant_to_query(variantes):
    """**Toma las variantes seleccionadas y regresa una cadena que filtra
    resultados de búsqueda por variantes**

    :param variantes: Lista de keys de las variantes seleccionadas
    :type: list
    :return: Cadena aceptada por el API de elasticsearch para filtrar
    :rtype: str
    """
    query = "("
    for i, variante in enumerate(variantes):
        # TODO: Mejorar la busqueda de variantes
        query += f"*{variante}*"
        if i == len(variantes) - 1:
            query += ")"
        else:
            query += " OR "
    return query


def results_to_csv(data, variants):
    """**Función que escribe los resultados de la consulta en archivo csv**

    Guarda los resultados de la consulta en formato ``csv`` en caso de
    que la usuaria quiera descargarlos.

    :param data_response: Resultados de la consulta devueltos
        por el índice de ``elasticsearch``
    :type: list
    :param variants: Variantes actuales para saber si escribir variante
        o dejar el campo vacío.
    :type: dict
    :return: Estatus del archivo. ``True`` si fue escrito, ``False`` en
        caso contrario
    :rtype: bool
    """
    row = []
    file_name = "query-results.csv"
    path_to_save = settings.BASE_DIR + settings.MEDIA_ROOT + file_name
    mappings = es.indices.get_mapping(index=settings.INDEX)
    del mappings[settings.INDEX]['mappings']['properties']['document_id']
    del mappings[settings.INDEX]['mappings']['properties']['pdf_file']
    del mappings[settings.INDEX]['mappings']['properties']['document_name']
    with open(path_to_save, "w") as csv_file:
        writer = csv.writer(csv_file)
        csv_header = list(mappings[settings.INDEX]['mappings']['properties'].keys())
        # Writing header
        writer.writerow(csv_header)
        for hit in data:
            result = hit["_source"]
            row = ["" for _ in range(len(csv_header))]
            for field in result:
                # Exclude fields when export query results to csv
                if field in ["document_id", "pdf_file", "document_name"]:
                    continue
                else:
                    header_position = csv_header.index(field)
                    row[header_position] = result[field]
            writer.writerow(row)
    return True


def ethno_table_maker(soup):
    """**Crea la tabla html con información de ethnologue**

    Con base en la variante en turno se crea, dinamicamente, una
    cadena que contiene una tabla html que será rendereada por un
    modal en la vista de busqueda.

    :param soup: Objeto con la página ``html`` de ethnologue
    :type: ``BeautifulSoup Object``
    :return: Tabla en formato ``html``
    :rtype: str
    """
    table = '<table class="table table-striped">'
    base = soup.find('div', class_='title-wrapper')
    title = soup.find('h1', id='page-title').text
    fields = base.find_all_next('div', class_='views-field')
    for i, field in enumerate(fields):
        if i == 0:
            table += f'''
            <thead>
                <tr class="table-info">
                    <th colspan="2"><h3>{title}</h3></th>
                </tr>
                <tr>
                    <th colspan="2">{field.text.strip()}</th>
                </tr>
            </thead>
            <tbody>
            '''
            continue
        content = field.find(class_='field-content').text
        content = content if content else '<i class="fa fa-lock">'
        table += f'''
            <tr>
                <th scope="row">
                    {field.find(class_='views-label').text}
                </th>
                <td>
                    {content}
                </td>
            </tr>
            '''
    table += "</tbody></table>"
    return table


def ethno_btn_maker(variante):
    """**Crea botones ``html`` con información ethnologue**

    Función encargada de construir los botones para la columna de
    variantes que despliegan los modals con la información obtenida
    de la plataforma ethnologue

    :param variante: Variante de la lengua 2
    :type: str
    :return: Cadenas con los botones en ``html``
    :rtype: str
    """
    iso = variante[variante.find('(')+1:variante.find(')')]
    btn_info = f'''
        <button type="button"
            class="badge badge-pill badge-info ethno-btn"
            data-toggle="modal" data-target="#ethnologue-table"
            onClick="ethnologueData('{iso}')"
            title="Ver información de la variante (Ethnologue)">
            <i class="fa fa-info"></i>
        </button>'''
    return variante + btn_info


def get_variants():
    """**Obtiene las variantes actuales de elasticsearch**

    Función encargada de obtener las variantes existentes en el índice
    de ``elasticsearch`` a través del API aggregations. Se obtienen en un
    diccionario con el ISO de la variante como llave y el nombre de
    la variante como valor. Se agrega al diccionario de variantes el
    estatus de la consulta (success o error).

    :return: variantes
    :rtype: dict
    """
    variants = {}
    variant_filters = {
        "size": 0,
        "aggs": {
            "variants": {
                "terms": {
                    # TODO: depende del header del CSV
                    "field": "variant",
                    "size": 100  # TODO: Cambiar dinamicamente
                }
            }
        }
    }
    try:
        response = es.search(index=settings.INDEX, body=variant_filters)
        results = response['aggregations']['variants']['buckets']
        for data in results:
            # Si la variante no es cadena vacía
            if data['key']:
                variant = data['key']
                # TODO: Manejar caso donde no haya ISO
                iso = variant[variant.find('(')+1:variant.find(')')]
                variants[iso] = variant
        variants['status'] = 'success'
    except es_exceptions.ConnectionError as e:
        LOGGER.error("No hay conexión a Elasticsearch::{}".format(e.info))
        LOGGER.error("No se pudo conectar al indice::" + settings.INDEX)
        LOGGER.error("URL::" + settings.ELASTIC_URL)
        # Diccionario porque se utilizara el metodo items() en forms
        variants = {'status': 'error'}
    except es_exceptions.NotFoundError:
        LOGGER.error("No se encontró el indice::" + settings.INDEX)
        LOGGER.error("URL::" + settings.ELASTIC_URL)
        variants = {'status': 'error'}
    return variants
