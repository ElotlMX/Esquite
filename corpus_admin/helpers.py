import os
import uuid
import csv
import json
import yaml
import logging
from django.conf import settings
from django.contrib import messages
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from elasticsearch import exceptions as es_exceptions

LOGGER = logging.getLogger(__name__)

# Cliente de `elasticsearch`
es = Elasticsearch([settings.ELASTIC_URL])


def get_corpus_info(request):
    """**Función que obtiene la información general del corpus**

    Está función utiliza el framework de ``Elasticsearch`` llamado
    *aggregations* para obtener los ids del corpus. Con cada uno se
    obtienen los nombres de documentos, nombres de archivos y total:>>.

    :return: El total de documentos y una lista con información de los
    documentos
    :rtype: int, list
    """
    ids_filters = {
        "size": 0,  # No interesan resultados del corpus. Solo los documentos
        "aggs": {
            "ids": {
                "terms": {
                    "field": "document_id",
                    "size": 1000  # TODO: Modificar la cantidad dinamicamente
                }
            }
        }
    }
    docs = []
    total = 0
    LOGGER.info("Buscando documentos")
    try:
        r = es.search(index=settings.INDEX, body=ids_filters)
        buckets = r['aggregations']['ids']['buckets']
        LOGGER.info("Documentos actuales::" + str(len(buckets)))
        for bucket in buckets:
            total += int(bucket["doc_count"])
            document = get_document_info(bucket['key'])
            document['count'] = bucket['doc_count']
            docs.append(document)
    except es_exceptions.ConnectionError as e:
        LOGGER.error("No hay conexión a Elasticsearch::{}".format(e.info))
        LOGGER.error("No se pudo conectar al indice::" + settings.INDEX)
        LOGGER.error("URL::" + settings.ELASTIC_URL)
        total = 0
        docs = []
        msg = f"No se pudo conectar al índice: <i>{settings.INDEX}</i>"
        messages.error(request, msg)
        msg = "TIP: ¿Está corriendo la instancia de Elasticsearch? ¿Existe el \
        índice?"
        messages.info(request, msg)
    except es_exceptions.NotFoundError:
        LOGGER.error("No se encontró el indice::" + settings.INDEX)
        LOGGER.error("URL::" + settings.ELASTIC_URL)
        total = 0
        docs = []
        msg = f"Parece que no existe el índice <b>{settings.INDEX}</b>"
        messages.warning(request, msg)
    return total, docs


def pdf_uploader(file, name):
    """**Función encargada de cargar y guardar el archivo pdf de un nuevo
    documento**

    :param file: ``pdf`` enviado por medio del objeto ``request``
    :type: ``FileField``
    :param name: Nombre del archivo PDF
    :type: str
    :return: Verdadero si se pudo cargar el archivo, falso en caso
        contrario
    :rtype: bool
    """
    LOGGER.info("Subiendo archivo PDF::{}".format(name))
    path_to_save = settings.BASE_DIR + settings.MEDIA_ROOT + name
    LOGGER.debug("Path de PDF::{}".format(path_to_save))
    with open(path_to_save, 'wb+') as destination:
        for i, chunk in enumerate(file.chunks()):
            destination.write(chunk)
    return True


def csv_writer(csv_file):
    """**Escribe un archivo ``csv`` de forma temporal**

    Esta función escribe el ``csv`` en disco para posteriormente
    subirlo al indice de ``Elasticsearch``

    :param csv_file: ``csv`` enviado por medio del objeto ``request``
    :type: ``FileField``
    :param file_name: Nombre del archivo ``csv``
    :type: str
    :return: ``True`` si se guardo correctamente
    :rtype: bool
    """
    LOGGER.debug(f"Guardando CSV temporal::{csv_file.name}")
    # Guardando en disco ante de procesar los datos
    with open(csv_file.name, 'wb+') as f:
        for chunk in csv_file.chunks():
            f.write(chunk)
    return True


def csv_reader(csv_filename):
    """**Lee datos del corpus paralelo de un archivo ``csv``**

    Esta función lee datos del corpus paralelo desde un archivo ``csv``.
    Devuelve un par de objetos, el header como lista y el contenido
    como cadena de texto.

    :param csv_filename: Nombre del archivo ``csv``
    :type csv_filename: str
    :return: Header del archivo y el contenido como texto plano
    :rtype: list, str
    """
    # TODO add exception
    with open(csv_filename, 'r', encoding='utf-8') as f:
        header = f.readline().lower().strip('\n').split(',')
        # Removing last new line
        csv_data = f.read().strip('\n')
    return header, csv_data


def csv_uploader(csv_name, doc_name, pdf_file, doc_id="", extra_fields=False):
    """**Función encargada de cargar nuevas líneas al corpus**

    Manipula los archivos mandados desde formulario y los carga al
    corpus de Tsunkua por medio del API de elasticsearch. Se espera que
    la primera columna del archivo csv sea el texto en español, la
    segunda columna sea el texto en otomí y la tercera columna sea la
    variante(s)

    :param csv_name: Nombre del archivo csv con el texto alineado
    :type: str
    :param doc_name: Nombre del documento a cargar
    :type: str
    :param pdf_file: Nombre del archivo PDF del documento
    :type: str
    :return: Número de líneas cargadas al corpus
    :rtype: int
    """
    LOGGER.info(f"Subiendo nuevo CSV::{csv_name}")
    # Subiendo al indice de Elasticsearch
    LOGGER.info(f"Subiendo al indice de Elasticsearch::{settings.INDEX}")
    with open(csv_name, 'r', encoding='utf-8') as f:
        raw_csv = f.read()
    # Si no existe el documento se crea un nuevo id
    if not doc_id:
        doc_id = str(uuid.uuid4()).replace('-', '')[:24]
    rows = raw_csv.split('\n')
    header = rows[0].lower().split(",")
    # Quitando cabecera del csv
    rows.pop(0)
    if extra_fields:
        # Toma en cuenta los campos del header del csv
        fields = header
    else:
        # Agrega solo los campos existentes en el indice
        fields = get_index_config()["mappings"]["properties"]
        fields = set(header).intersection(set(fields))
    res = bulk(es, data_generator(rows, fields, doc_name, pdf_file, doc_id, header))
    LOGGER.info(f"Lineas agreadas::{res[0]}")
    if res[1]:
        LOGGER.warning(f"Lineas erroneas::{res[1]}")
    LOGGER.debug(f"Eliminando csv temporal::{csv_name}")
    os.remove(csv_name)
    return len(rows)


def data_generator(data_rows, fields, doc_name, pdf_file, doc_id, header):
    """**Genera los datos a ser indexados**

    :param data_rows: Lista de lineas del archivo csv
    :type data_rows: list
    :param fields: Columnas del csv
    :type fields: list
    """
    for text in csv.reader(data_rows, delimiter=',', quotechar='"'):
        # Check blank line
        if text:
            # If there are text in lang 1 and lang 2 then index data
            if text[header.index("l1")] and text[header.index("l2")]:
                document = {
                    "_index": settings.INDEX,
                    "pdf_file": pdf_file,
                    "document_id": doc_id,
                    "document_name": doc_name,

                }
                for field in fields:
                    if field in ["document_name", "pdf_file", "document_id"]:
                        continue
                    else:
                        document[field] = text[header.index(field)]
                yield document
        else:
            msg = "Omitiendo linea en blanco"
            LOGGER.warning(msg)


def get_document_info(_id):
    """**Obtiene información de un documento de Elasticsearch**

    Función encargada de obtener el nombre de documento,
    nombre del archivo asociado al documento e identificador
    por medio del id

    :param _id: Identificador del documento
    :type: str
    :return: Diccionario con nombre, archivo e identificador
    :rtype: dict
    """
    query_base = {
        "version": True, "size": 1,
        "query": {
            "query_string": {
                "query": 'document_id:' + _id,
                "analyze_wildcard": True
            }
        }
    }
    r = es.search(index=settings.INDEX, body=query_base)
    if r['hits']['hits']:
        data = r['hits']['hits'][0]['_source']
    else:
        LOGGER.error("Data not found ID::{}".format(_id))
        data = {"name": "Not Found", "pdf_file": "Not Found",
                "document_name": "Not_Found"}
    name = data['document_name']
    file = data['pdf_file']
    # TODO: Agregar mas información útil
    return {"name": name, "file": file, "id": _id}


def check_extra_fields(fields, full=False):
    """Revisa si existen campos adicionales a los default

    :param fields: Campos del usuario presentes en la cabecera del ``csv``
    :type: list
    :param full: Bandera opcional si se requieren los campos completos. Por
    ejemplo cuando se sube un respaldo de la base de datos
    :type: bool
    :return: Los campos adicionales encontrados si existen
    :rtype: set
    """
    # If user already create custom configurations
    if os.path.isfile('user-elastic-config.json'):
        with open('user-elastic-config.json') as json_file:
            configs = json.loads(json_file.read())
    # Using default configurations
    else:
        with open('elastic-config.json') as json_file:
            configs = json.loads(json_file.read())
    default_fields = configs['mappings']['properties'].keys()
    if full:
        # Remove additional fields
        del default_fields['document_id']
        del default_fields['document_name']
        del default_fields['pdf_file']
    # Aditional fields
    if set(fields) - set(default_fields) != set():
        aditional_fields = set(fields) - set(default_fields)
    else:
        aditional_fields = set()
    return aditional_fields


def update_config(config):
    """Actualiza las configuraciones locales de elasticsearch

    """
    with open('user-elastic-config.json', 'w') as json_file:
        json.dump(config, json_file, indent=2)
    return 0


def update_index_name(new_index_name):
    with open("env.yaml", 'r') as f:
        env_configs = yaml.load(f, Loader=yaml.FullLoader)
        env_configs['INDEX'] = new_index_name
    with open("env.yaml", 'w') as f:
        yaml.dump(env_configs, f)
    settings.INDEX = new_index_name
    return 0


def get_index_config():
    # If user already create custom configurations
    if os.path.isfile('user-elastic-config.json'):
        with open('user-elastic-config.json') as json_file:
            configs = json.loads(json_file.read())
    # Using default configurations
    else:
        with open('elastic-config.json') as json_file:
            configs = json.loads(json_file.read())
    return configs
