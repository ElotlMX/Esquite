# --------------------------------------
import logging
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from .forms import NewDocumentForm, DocumentEditForm, AddDocumentDataForm
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
            return HttpResponseRedirect("/corpus-admin/")
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
    current_variants = get_variants()
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
            set_name, set_file = '', ''
            # Script que se ejecutara en Elasticsearch
            base_script = "ctx._source.put('document_"
            if data_form['nombre'] != '':
                set_name = base_script + f"name', '{data_form['nombre']}');"
                notification = f"""El documento <b>{_id}</b> cambió el nombre
                a <b>{data_form['nombre']}</b>."""
                messages.add_message(request, messages.WARNING, notification)

            if data_form['pdf'] is not None:
                set_file = base_script + f"file', '{data_form['pdf'].name}');"
                pdf_uploader(data_form['pdf'], data_form['pdf'].name)
                notification = f"""El archivo del documento <b>{_id}</b> PDF
                cambió a <b>{data_form['pdf'].name}</b>."""
                messages.add_message(request, messages.WARNING, notification)

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
                messages.add_message(request, messages.ERROR, notification)
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
    if request.method == "POST":
        document_id = request.POST.get('doc_id')
        query = {"query": {"term": {"document_id": document_id}}}
        r = es.delete_by_query(index=settings.INDEX, body=query, refresh=True)
        LOGGER.debug("# lineas borradas::{}".format(r['deleted']))
        notification = f"{r['deleted']} líneas borradas de {document_id}"
        messages.info(request, notification)
        return HttpResponseRedirect("/corpus-admin/")
