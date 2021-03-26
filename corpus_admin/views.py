import os
import csv
import logging
import json
import datetime
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from .forms import (NewDocumentForm, DocumentEditForm, AddDocumentDataForm,
                   IndexConfigForm)
from .helpers import (get_corpus_info, pdf_uploader, csv_uploader,
                      get_document_info, csv_writer, check_extra_fields,
                      update_config, update_index_name, get_index_config)
from searcher.helpers import (data_processor, doc_file_to_link, get_variants,
                              query_kreator)
from elasticsearch import Elasticsearch
from elasticsearch import exceptions as es_exceptions

LOGGER = logging.getLogger(__name__)

# Cliente de `elasticsearch`
es = Elasticsearch([settings.ELASTIC_URL])


def list_docs(request):
    """
    **Esta vista muestra todos los documentos que conforman el corpus
    paralelo**

    * `:param request:` Objeto *HttpRequets* para pasar el estado de la app a
        través del sistema
    * `:type:` *HttpRequest*
    * `:return:` Lista de documentos del corpus con acciones por documento
    """
    # Errores en las variables de entorno del proyecto
    breakpoint()
    if settings.WRONG_CONFIGS['error']:
        msg = "Configuraciones necesarias para sitio no se encuentran en \
        el archivo <code>env.yaml</code>."
        str_fields = ", ".join(settings.WRONG_CONFIGS['error'])
        msg += f" Modifica los campos: {str_fields} o ejecuta el asistente \
            <code>wizard.py</code>."
        messages.error(request, msg)
        conf_docs_link = "https://esquite.readthedocs.io/es/latest/wizard.html#configuraciones"
        messages.info(request, f"TIP: Revisar la documentación <a href='{conf_docs_link}'>aqui<a>")
    if "COLORS" in settings.WRONG_CONFIGS['warn']:
        messages.warning(request, "Los colores del proyecto no fueron \
                         configurados")
    total, docs = get_corpus_info(request)
    variants = get_variants()
    del variants['status']
    LOGGER.info("Total::{}".format(total))
    return render(request, "corpus-admin/docs-list.html",
                  {'total': total, 'docs': docs, 'variants': variants})


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
            csv_writer(data_form['csv'])
            csv_file_name = data_form['csv'].name
            pdf_uploader(data_form['pdf'], data_form['pdf'].name)
            with open(csv_file_name, 'r', encoding='utf-8') as f:
                header = f.readline().lower().strip('\n').split(',')
                # Removing last new line
                csv_file = f.read().strip('\n')
            extra_fields = check_extra_fields(header)
            if extra_fields:
                rows = csv_file.split('\n')
                total_lines = len(rows)
                notification = f"Detectamos los campos adicionales: {', '.join(extra_fields)}"
                messages.warning(request, notification)
                pre_rows = rows[:5]
                pre_rows = [txt for txt in csv.reader(pre_rows,  delimiter=',', quotechar='"')]
                return render(request, "corpus-admin/extra-fields.html",
                              {"fields": extra_fields, 'doc_name':
                               data_form['nombre'], 'pdf_file':
                               data_form['pdf'].name, 'total_lines':
                               total_lines, 'preview_lines': pre_rows,
                               'header': header, 'csv_file_name': csv_file_name})

            else: # Upload the csv file as usual
                if os.path.isfile(csv_file_name):
                    LOGGER.info(f"El archivo {csv_file_name} ya existe.")
                else:
                    if csv_file.multiple_chunks():
                        LOGGER.warning("Documento grande {:.2f}MB".format(
                            csv_file.size / (1000 * 1000)))
                    csv_writer(data_form['csv'])
                lines = csv_uploader(csv_file_name, data_form['nombre'],
                                     data_form['pdf'].name)
                # TODO: Checar si existe el archivo antes de subirlo
                notification = 'El documento <b>' + data_form['nombre'] + \
                               '</b> fue guardado correctamente. <b>' + \
                               str(lines) + ' líneas</b> agregadas al corpus.'
                messages.add_message(request, messages.INFO, notification)
                return HttpResponseRedirect('/corpus-admin/new/')
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
    # TODO: Make a function for this
    mappings = es.indices.get_mapping(index=settings.INDEX)
    del mappings[settings.INDEX]['mappings']['properties']['document_id']
    del mappings[settings.INDEX]['mappings']['properties']['pdf_file']
    del mappings[settings.INDEX]['mappings']['properties']['document_name']
    fields = list(mappings[settings.INDEX]['mappings']['properties'].keys())
    # Ordening fields
    fields.insert(0, fields.pop(fields.index("l1")))
    fields.insert(1, fields.pop(fields.index("l2")))
    fields.insert(2, fields.pop(fields.index("variant")))
    return render(request, "corpus-admin/doc-preview.html",
                  {
                      "doc_data": corpus, "doc_name": name,
                      "doc_file": file, "total": len(corpus),
                      "id": _id, "total_variants": len(current_variants),
                      "fields": fields
                  })


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
            csv_writer(data_form['csv'])
            # TODO: Check extra fields
            lines = csv_uploader(data_form['csv'].name,
                                 doc['name'],
                                 doc['file'],
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
    """**Vista que exporta la base de datos completa del índice**

    Vista llamada desde el botón de *exportar* en el administrador del corpus.
    Se genera un respaldo de la base de datos en formato ``csv`` con el que se
    puede restaurar en otro índice de Elasticsearch.

    * `:param request:` Objeto *HttpRequets* para pasar el estado de la app a
        través del sistema
    * `:type:` *HttpRequest*
    """
    project_name = settings.NAME
    # Setting file metadata
    response = HttpResponse(content_type="text/csv")
    date = datetime.datetime.now()
    format_date = date.strftime("%d-%m-%Y")
    response['Content-Disposition'] = f"attachment;filename={project_name}-bkp-{format_date}.csv"
    writer = csv.writer(response)
    mappings = es.indices.get_mapping(index=settings.INDEX)
    csv_header = list(mappings[settings.INDEX]['mappings']['properties'].keys())
    # Getting all data from index
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
        else:
            # Filling list to sort csv row text later
            row = ["" for _ in range(len(csv_header))]
            for field in data:
                # Sorting text on row by header position
                header_position = csv_header.index(field)
                row[header_position] = data[field]
        writer.writerow(row)
    return response


def index_config(request):
    """**Configura un índice de elasticsearch**

    Permite configurar o modificar la configuración de un índice de
    elasticsearch por medio de un formulario.

    :returns: None
    """
    default_fields = ["l1", "l2", "variant", "document_name", "pdf_file"]
    if request.method == "POST":
        data = request.POST
        # Aditional fields
        if set(fields) - set(default_fields) != set():
            aditional_fields = set(fields) - set(default_fields)
        else:
            aditional_fields = []
            notification = "No detectamos ningun campo adicional en el archivo CSV que subiste :o"
            messages.warning(request, notification)
            messages.info(request, f"Campos mínimos: {', '.join(default_fields)}")
        with open("elastic-config.json", 'r') as f:
            json_file = f.read()
        data_config = json.loads(json_file)
        for optional_field in aditional_fields:
            data_config['mappings']['properties'][optional_field] = {'type': 'keyword'}
        index_name = settings.INDEX
        form = IndexConfigForm()
        return render(request, "corpus-admin/index-config.html",
                      {
                          "form": form, "index_name": index_name,
                          'aditional_fields': aditional_fields,
                      })
    else:
        analysis = {"idioma": "spanish"}
        fields = dict()
        # Just visualize the current configuration
        config = get_index_config()
        index_config = config['settings']['index']
        analyzer = index_config['analysis']['analyzer']
        analyzer_name = list(analyzer.keys())[0]
        analysis['filtros'] = analyzer[analyzer_name]['filter']
        analysis['nombre'] = analyzer_name
        mappings = config['mappings']
        fields = mappings['properties']
        index_name = settings.INDEX
        return render(request, "corpus-admin/index-config.html",
                      {
                        "index_name": index_name, 'mappings': mappings,
                        'index_config': index_config, 'analysis': analysis,
                        'fields': fields,
                      })


def extra_fields(request, csv_file_name, document_name, pdf_file_name):
    """Configura los campos extra detectados en un ``CSV``

    :param request: Objeto ``HttpRequets`` de Django
    :type request: HttpRequest
    :param csv_file_name: Nombre del archivo ``csv``
    :type csv_file_name: str
    :param document_name: Nombre del documento
    :type document_name: str
    :param pdf_file_name: Nombre del archivo ``pdf``
    :type pdf_file_name: str
    :return: Redirecciona a la vista de nuevo documento
    :rtype: None
    """
    if request.method == "POST":
        has_extra_fields = False
        if "config-fields-switch" in request.POST:
            data = dict(request.POST)
            del data['config-fields-switch']
            del data['csrfmiddlewaretoken']
            configs = get_index_config()
            for field, field_type in data.items():
                configs['mappings']['properties'][field] = {'type': field_type[0]}
            try:
                es.indices.put_mapping(configs['mappings'], index=settings.INDEX)
            except es_exceptions.RequestError as e:
                messages.error(request, "Error al configurar índice :(")
                # TODO: Tell to the user that something goes wrong!
                print(e)
            new_mappings = es.indices.get_mapping(index=settings.INDEX)
            configs['mappings'] = new_mappings[settings.INDEX]['mappings']
            update_config(configs)
            has_extra_fields = True
            messages.add_message(request,
                                 messages.SUCCESS,
                                 f"Los campos extra <b>\
                                 {', '.join(data.keys())}\
                                 </b>fueron configurados exitosamente")
        # Upload document as usual
        lines = csv_uploader(csv_file_name, document_name, pdf_file_name,
                             extra_fields=has_extra_fields)
        notification = 'El documento <b>' + document_name + \
                       '</b> fue guardado correctamente. <b>' + \
                       str(lines) + ' líneas</b> agregadas al corpus.'
        messages.add_message(request, messages.INFO, notification)
        return HttpResponseRedirect('/corpus-admin/new/')
    else:
        return HttpResponseRedirect("/corpus-admin/new/")
