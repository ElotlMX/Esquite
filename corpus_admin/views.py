import csv
import logging
import json
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from .forms import (NewDocumentForm, DocumentEditForm, AddDocumentDataForm,
                   IndexConfigForm)
from .helpers import (get_corpus_info, pdf_uploader, csv_uploader,
                      get_document_info)
from searcher.helpers import (data_processor, doc_file_to_link, get_variants,
                              query_kreator)
from elasticsearch import Elasticsearch

LOGGER = logging.getLogger(__name__)

# Cliente de `elasticsearch`
es = Elasticsearch([settings.ELASTIC_URL])

# === Listar documentos ===


def list_docs(request):
    """
    **Esta vista muestra todos los documentos que conforman el corpus
    paralelo**

    * `:param request:` Objeto *HttpRequets* para pasar el estado de la app a
        través del sistema
    * `:type:` *HttpRequest*
    * `:return:` Lista de documentos del corpus con acciones por documento
    """
    # TODO: Excepcion cuando no se pueda conectar al indice del corpus
    LOGGER.info("Listando Documentos")
    total, docs = get_corpus_info()
    variants = get_variants()
    # TODO: Notificar de error al traer variantes
    del variants['status']
    LOGGER.info("Total::{}".format(total))
    return render(request, "corpus-admin/docs-list.html",
                  {'total': total, 'docs': docs, 'variants': variants})

# === Nuevo Documento ===


def new_doc(request):
    """
    **Vista que muestra el formulario para cargar nuevos documentos al
    corpus**

    Vista encargada de mostrar el formulario para agregar nuevo
    documentos al corpus. El documento se compone de archivo `CSV`
    alineado, PDF como portada del corpus y el nombre del archivo. En
    caso de éxito al subir el documento se redirige a la lista de
    documentos.

    * `:param request:` Objeto *HttpRequets* para pasar el estado de la app a
        través del sistema
    * `:type:` *HttpRequest*
    * `:return:` Vista con formulario para nuevos documentos
    """
    if request.method == "POST":
        form = NewDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            data_form = form.cleaned_data
            lines = csv_uploader(data_form['csv'], data_form['nombre'],
                                     data_form['pdf'].name)
            pdf_uploader(data_form['pdf'], data_form['pdf'].name)
            # TODO: Checar si existe el archivo antes de subirlo
            # TODO: Barra de progreso de subida
            notification = 'El documento <b>' + data_form['nombre'] + \
                           '</b> fue guardado correctamente. <b>' + \
                           str(lines) + ' líneas</b> agregadas al corpus.'
            messages.add_message(request, messages.INFO, notification)
            return HttpResponseRedirect('/corpus-admin/')
        else:
            if "nombre" in form.errors:
                form.fields["nombre"].widget.attrs["class"] += " is-invalid"
            else:
                form.fields["nombre"].widget.attrs["class"] += " is-valid"
            messages.error(request, "Llena todos los campos")
            return render(request, "corpus-admin/new-doc.html", {'form': form})
    else:
        form = NewDocumentForm()
        return render(request, "corpus-admin/new-doc.html", {'form': form})

# === Contenido de documentos ===


def doc_preview(request, _id):
    """**Vista que muestra el contenido de un documento particular**

    Muestra los renglones alineados que componen un documento en
    particular del corpus. Cada renglon tiene dos acciones, eliminar y
    editar.

    * `:param request:` Objeto *HttpRequets* para pasar el estado de la app a
        través del sistema
    * `:type:` *HttpRequest*
    * `:param _id:` identificador del documento a visualizar
    * `:type:` *str*
    * `:return:` Contenido de un documento
    """
    query = query_kreator("document_id:" + _id)
    r = es.search(index=settings.INDEX, body=query)
    corpus = data_processor(r['hits'], "NONE", "")
    data = r['hits']['hits'][0]['_source']
    name = data['document_name']
    doc = get_document_info(_id)
    file = doc['file']
    # TODO: Refactor variants across the backend
    current_variants = get_variants()
    if len(current_variants) == 1:
        current_variants = {}
    return render(request, "corpus-admin/doc-preview.html",
                  {
                      "doc_data": corpus, "doc_name": name,
                      "doc_file": file, "total": len(corpus),
                      "id": _id, "total_variants": len(current_variants)
                  })

# === Edición de documentos ===


def doc_edit(request, _id):
    """
    **Vista que muestra el formulario para editar el nombre y pdf de un
    documento**

    * `:param request:` Objeto *HttpRequets* para pasar el estado de la app a
        través del sistema
    * `:type:` *HttpRequest*
    * `:param _id:` Identificador de documento
    * `:type:` *str*
    * `:return:` Formulario para editar el nombre y pdf de un documento
    """
    if request.method == "POST":
        form = DocumentEditForm(request.POST, request.FILES)
        if form.is_valid():
            data_form = form.cleaned_data
            # Script que se ejecutara en Elasticsearch
            if data_form['nombre'] != '':
                doc_name = data_form['nombre']
                set_name = f"ctx._source.put('document_name', '{doc_name}');"
                notification = f"""El documento <b>{_id}</b> cambió el nombre
                a <b>{doc_name}</b>."""
                messages.add_message(request, messages.WARNING, notification)
            else:
                set_name = ''

            if data_form['pdf'] is not None:
                pdf_name = data_form['pdf'].name
                set_file = f"ctx._source.put('pdf_file', '{pdf_name}');"
                pdf_uploader(data_form['pdf'], pdf_name)
                notification = f"""El archivo del documento <b>{_id}</b> PDF
                cambió a <b>{pdf_name}</b>."""
                messages.add_message(request, messages.WARNING, notification)
            else:
                set_file = ''

            if set_file or set_name:
                update_rules = {
                    "script": {
                        "source": set_name + set_file,
                        "lang": "painless"
                    },
                    "query": {
                        "term": {
                            "document_id": _id
                        }
                    }
                }
                es.update_by_query(index=settings.INDEX, body=update_rules)
                return HttpResponseRedirect('/corpus-admin/')
            else:
                notification = "Se debe modificar <b>al menos un campo</b>. " \
                               "Documento sin cambios :("
                messages.add_message(request, messages.WARNING, notification)
                return HttpResponseRedirect('/corpus-admin/edit/' + _id)
    else:
        form = DocumentEditForm()
        doc = get_document_info(_id)
        return render(request, "corpus-admin/doc-edit.html",
                      {
                          "form": form, "doc_name": doc['name'],
                          "doc_file": doc['file'],
                          "id": _id
                      })

# === Agregar lineas a documento ===


def add_doc_data(request, _id):
    """
    **Vista que muestra un formulario para añadir líneas a un documento
    existente**

    * `:param request:` Objeto *HttpRequets* para pasar el estado de la app a
        través del sistema
    * `:type:` *HttpRequest*
    * `:param _id:` identificador del documento a visualizar
    * `:type:` *str*
    * `:return:` Formulario para agregar líneas a un documento existente
    """
    if request.method == "POST":
        form = AddDocumentDataForm(request.POST, request.FILES)
        if form.is_valid():
            data_form = form.cleaned_data
            doc = get_document_info(_id)
            lines = csv_uploader(data_form['csv'], doc['name'], doc['file'],
                                _id)
            notification = 'El documento <b>' + doc['name'] + \
                           '</b> fue actualizado correctamente. <b>' + \
                           str(lines) + ' líneas</b> agregadas.'
            messages.add_message(request, messages.INFO, notification)
            return HttpResponseRedirect("/corpus-admin/")
    else:
        form = AddDocumentDataForm()
        doc = get_document_info(_id)
        return render(request, "corpus-admin/add-rows.html",
                      {
                          "form": form, "doc_name": doc['name'],
                          "doc_file": doc['file'],
                          "id": _id
                      })

# === Borrar documentos ===


def delete_doc(request):
    """**Vista encargada de eliminar documentos del corpus**

    * `:param request:` Objeto *HttpRequets* para pasar el estado de la app a
        través del sistema
    * `:type:` *HttpRequest*
    """
    # TODO: Agregar excepcion cuando haya error de conexion
    if request.method == "POST":
        document_id = request.POST.get('doc_id')
        query = {"query": {"term": {"document_id": document_id}}}
        r = es.delete_by_query(index=settings.INDEX, body=query, refresh=True)
        LOGGER.debug("# lineas borradas::{}".format(r['deleted']))
        notification = f"{r['deleted']} líneas borradas de {document_id}"
        messages.info(request, notification)
        return HttpResponseRedirect("/corpus-admin/")


def export_data(request):
    project_name = settings.NAME
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f"attachment; filename={project_name}-data.csv"
    writer = csv.writer(response)
    csv_header = ["l1", "l2", "variant", "document_name",
                  "pdf_file", "document_id"]
    query = '{"query": {"match_all": {}}}'
    r = es.search(index=settings.INDEX, body=query, scroll="1m", size=1000)
    data_response = r["hits"]
    scroll_id = r["_scroll_id"]
    total_rows = data_response["total"]["value"]
    rows_count = len(data_response["hits"])
    while rows_count != total_rows:
        sub_response = es.scroll(scroll_id=scroll_id, scroll="1m")
        data_response["hits"] += sub_response["hits"]["hits"]
        rows_count += len(sub_response["hits"]["hits"])
        scroll_id = sub_response["_scroll_id"]
    writer.writerow(csv_header)
    for hit in data_response["hits"]:
        row = []
        data = hit['_source']
        fields = data.keys()
        if "l1" not in fields or "l2" not in fields:
            LOGGER.warning(f"Linea {hit['_id']} en blanco. Se omite")
            continue
        elif "variant" not in fields:
            row.append(data["l1"])
            row.append(data["l2"])
            row.append("")
            row.append(data["document_name"])
            row.append(data["pdf_file"])
            row.append(data["document_id"])
        else:
            row.append(data["l1"])
            row.append(data["l2"])
            row.append(data["variant"])
            row.append(data["document_name"])
            row.append(data["pdf_file"])
            row.append(data["document_id"])
        writer.writerow(row)
    return response


def index_config(request):
    """Configura un índice de elasticsearch

    Permite configurar o modificar la configuración de un índice de
    elasticsearch por medio de un formulario.

    :returns: None
    """
    with open("elastic-config.json", 'r') as f:
        json_file = f.read()
    data = json.loads(json_file)
    index_name = settings.INDEX
    form = IndexConfigForm(initial={'index_name': index_name,
                                    'settings': json.dumps(data['settings'],
                                                           indent=2,
                                                           sort_keys=True),
                                    'mapping': json.dumps(data['mappings'],
                                                          indent=2,
                                                         sort_keys=True)})
    return render(request, "corpus-admin/index-config.html",
                  {
                      "form": form, "index_name": index_name
                  })
