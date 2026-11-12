import csv
import json
import logging
import os
import tempfile
import uuid
from pathlib import Path

import yaml
from django.conf import settings
from django.contrib import messages
from django.core.files.uploadedfile import UploadedFile
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as es_exceptions
from elasticsearch.helpers import bulk

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
                    "size": 1000,  # TODO: Modificar la cantidad dinamicamente
                }
            }
        },
    }
    docs = []
    total = 0
    LOGGER.info("Buscando documentos")
    try:
        r = es.search(index=settings.INDEX, body=ids_filters)
        buckets = r["aggregations"]["ids"]["buckets"]
        LOGGER.info("Documentos actuales::" + str(len(buckets)))
        for bucket in buckets:
            total += int(bucket["doc_count"])
            document = get_document_info(bucket["key"])
            document["count"] = bucket["doc_count"]
            docs.append(document)
    except es_exceptions.ConnectionError as e:
        LOGGER.error(f"No hay conexión a Elasticsearch:: {e}")
        LOGGER.error(f"No se pudo conectar al indice:: {settings.INDEX}")
        LOGGER.error(f"URL:: {settings.ELASTIC_URL}")
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
    :return: Nombre real del archivo guardado; si ya existía un PDF con el
        mismo nombre se agrega un sufijo (``nombre_1.pdf``) para no
        sobrescribirlo
    :rtype: str
    """
    LOGGER.info(f"Subiendo archivo PDF:: {name}")
    stem, ext = os.path.splitext(name)
    counter = 1
    path_to_save = settings.BASE_DIR + settings.MEDIA_ROOT + name
    while os.path.exists(path_to_save):
        name = f"{stem}_{counter}{ext}"
        path_to_save = settings.BASE_DIR + settings.MEDIA_ROOT + name
        counter += 1
    LOGGER.debug(f"Path de PDF:: {path_to_save}")
    with open(path_to_save, "wb+") as destination:
        destination.writelines(file.chunks())
    return name


def save_csv_temporarily(csv_file: UploadedFile) -> Path | None:
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
    if not hasattr(csv_file, "chunks"):
        LOGGER.error(
            f"Objeto de archivo inválido: Se esperaba un UploadedFile con método .chunks(), se recibió {type(csv_file)}"
        )
        return None

    LOGGER.debug(f"Guardando CSV temporal::{csv_file.name}")

    try:
        # Creamos un archivo temporal
        # delete=False es necesario para que el archivo persista
        # después de cerrar el contexto y pueda ser leído por Elasticsearch.
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
            for chunk in csv_file.chunks():
                tmp_file.write(chunk)

            return Path(tmp_file.name)
    except PermissionError:
        LOGGER.error(
            f"Permiso denegado al intentar escribir {csv_file.name}.csv en disco"
        )
    except OSError as e:
        LOGGER.error(f"Error I/O del OS al guardar el CSV temporal: {e}")
    except Exception as e:
        LOGGER.exception(f"Error inesperado al guardar CSV temporal: {e}")
    return None


def header_normalizer(header: str) -> list:
    """**Normaliza la cabecera del archivo ``csv``**

    Esta función normaliza la cabecera del archivo ``csv``. Convierte
    todos los caracteres a minúsculas y elimina espacios en blanco.
    Además rechaza nombres vacíos, columnas duplicadas y cabeceras sin
    las columnas obligatorias ``l1`` y ``l2``.

    :param header: Cabecera del archivo ``csv``
    :type: str
    :return: Cabecera normalizada como lista
    :rtype: list
    """
    if not isinstance(header, str):
        LOGGER.error(
            f"Se esperaba un string para la cabecera, se recibió {type(header)}"
        )
        raise ValueError("La cabecera debe ser un string")

    if not header:
        LOGGER.warning("Se recibió una cabecera vacía")
        raise ValueError("La cabecera no puede estar vacía")

    header_list = [h.strip().lower() for h in next(csv.reader([header]), [])]

    # Reject blank column names (e.g. trailing comma or ",," in the line)
    if any(not name for name in header_list):
        LOGGER.error(
            f"La cabecera del CSV contiene nombres de columna vacíos. Columnas encontradas: {header_list}"
        )
        raise ValueError("La cabecera del CSV contiene nombres de columna vacíos")

    # Check if the header is empty after normalization
    if not header_list:
        LOGGER.error("La cabecera del CSV está vacía después de la normalización")
        raise ValueError(
            "La cabecera del CSV no puede estar vacía después de la normalización"
        )

    # Check l1 and l2 columns
    if "l1" not in header_list or "l2" not in header_list:
        LOGGER.error(
            f"La cabecera del CSV debe contener las columnas 'l1' y 'l2'. Columnas encontradas: {format(header_list)}"
        )
        raise ValueError(
            f"La cabecera del CSV debe contener las columnas 'l1' y 'l2'. Columnas encontradas: {format(format(header_list))}"
        )

    # Reject duplicate columns in the header
    if len(header_list) != len(set(header_list)):
        LOGGER.error(
            f"La cabecera del CSV contiene columnas duplicadas. Columnas encontradas: {format(header_list)}"
        )
        raise ValueError("La cabecera del CSV contiene columnas duplicadas")

    return header_list


def csv_reader(csv_filename: Path) -> tuple[list, str]:
    """**Lee datos del corpus paralelo de un archivo ``csv``**

    Esta función lee datos del corpus paralelo desde un archivo ``csv``.
    Devuelve un par de objetos, el header como lista y el contenido
    como cadena de texto.

    :param csv_filename: Nombre del archivo ``csv``
    :type csv_filename: str
    :return: Header del archivo y el contenido como texto plano
    :rtype: list, str
    """
    try:
        with open(csv_filename, "r", encoding="utf-8") as f:
            header = header_normalizer(f.readline())
            csv_data = f.read().strip("\n")
    except FileNotFoundError:
        LOGGER.error(f"Archivo CSV no encontrado: {csv_filename}")
        raise
    except Exception as e:
        LOGGER.exception(f"Error al leer el archivo CSV {csv_filename}: {e}")
        raise
    return header, csv_data


def csv_uploader(csv_path, doc_name, pdf_file, doc_id="", extra_fields=False):
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
    LOGGER.info(f"Subiendo nuevo CSV::{csv_path}")
    # Subiendo al indice de Elasticsearch
    LOGGER.info(f"Subiendo al indice de Elasticsearch::{settings.INDEX}")
    header, csv_data = csv_reader(csv_path)

    # Si no existe el documento se crea un nuevo id
    if not doc_id:
        doc_id = str(uuid.uuid4()).replace("-", "")[:24]

    if extra_fields:
        # Toma en cuenta los campos del header del csv
        fields = header
    else:
        # Agrega solo los campos existentes en el indice
        fields = get_index_config()["mappings"]["properties"]
        fields = set(header).intersection(set(fields))

    # Convierte el contenido del csv en una lista de lineas
    rows = csv_data.split("\n")
    res = bulk(es, data_generator(rows, fields, doc_name, pdf_file, doc_id, header))
    LOGGER.info(f"Lineas agreadas::{res[0]}")
    if res[1]:
        LOGGER.warning(f"Lineas erroneas::{res[1]}")
    LOGGER.debug(f"Eliminando csv temporal::{csv_path}")
    os.remove(csv_path)
    return len(rows)


def data_generator(
    data_rows: list,
    fields: list,
    doc_name: str,
    pdf_file: str,
    doc_id: str,
    header: list,
):
    """**Genera los datos a ser indexados**

    :param data_rows: Lista de lineas del archivo csv
    :type data_rows: list
    :param fields: Columnas del csv
    :type fields: list
    :param doc_name: Nombre del documento
    :type doc_name: str
    :param pdf_file: Nombre del archivo PDF
    :type pdf_file: str
    :param doc_id: Identificador del documento
    :type doc_id: str
    :param header: Cabecera del archivo csv
    :type header: list
    :yield: Diccionario con los datos a indexar
    :rtype: dict
    """
    for text in csv.reader(data_rows, delimiter=",", quotechar='"'):
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
        "version": True,
        "size": 1,
        "query": {
            "query_string": {"query": "document_id:" + _id, "analyze_wildcard": True}
        },
    }
    r = es.search(index=settings.INDEX, body=query_base)
    if r["hits"]["hits"]:
        data = r["hits"]["hits"][0]["_source"]
    else:
        LOGGER.error("Data not found ID::{}".format(_id))
        data = {
            "name": "Not Found",
            "pdf_file": "Not Found",
            "document_name": "Not_Found",
        }
    name = data["document_name"]
    file = data["pdf_file"]
    # TODO: Agregar mas información útil
    return {"name": name, "file": file, "id": _id}


def check_extra_fields(fields, full=False) -> set:
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
    if os.path.isfile("user-elastic-config.json"):
        with open("user-elastic-config.json") as json_file:
            configs = json.loads(json_file.read())
    # Using default configurations
    else:
        with open("elastic-config.json") as json_file:
            configs = json.loads(json_file.read())
    default_fields = configs["mappings"]["properties"].keys()
    if full:
        # Remove additional fields
        del default_fields["document_id"]
        del default_fields["document_name"]
        del default_fields["pdf_file"]

    # Aditional fields
    if set(fields) - set(default_fields) != set():
        aditional_fields = set(fields) - set(default_fields)
    else:
        aditional_fields = set()
    return aditional_fields


def update_config(config):
    """Actualiza las configuraciones locales de elasticsearch"""
    with open("user-elastic-config.json", "w") as json_file:
        json.dump(config, json_file, indent=2)
    return 0


def update_index_name(new_index_name):
    with open("env.yaml", "r") as f:
        env_configs = yaml.load(f, Loader=yaml.FullLoader)
        env_configs["INDEX"] = new_index_name
    with open("env.yaml", "w") as f:
        yaml.dump(env_configs, f)
    settings.INDEX = new_index_name
    return 0


def get_index_config():
    # If user already create custom configurations
    if os.path.isfile("user-elastic-config.json"):
        with open("user-elastic-config.json") as json_file:
            configs = json.loads(json_file.read())
    # Using default configurations
    else:
        with open("elastic-config.json") as json_file:
            configs = json.loads(json_file.read())
    return configs
