import os
import logging
from git import Repo, exc
from django.shortcuts import render
from corpus_admin.helpers import get_corpus_info, get_variants
from django.http import FileResponse, Http404
from django.conf import settings
from django.contrib import messages
from searcher.forms import SearchPostForm

LOGGER = logging.getLogger(__name__)


def index(request):
    """**Muestra la vista raíz del corpus paralelo**

    :param request: Objeto ``HttpRequets`` para pasar el estado de la app
                    a través del sistema
    :type: ``HttpRequest``
    :return: Vista principal
    """
    LOGGER.info("Entrando a index")
    # Formulario de búsqueda en django
    form = SearchPostForm()
    # Agregando variantes desde el servidor
    current_variants = get_variants()
    if current_variants['status'] == 'success':
        del current_variants['status']
        if len(current_variants):
            LOGGER.debug("Variantes actuales: " + ", ".join(list(current_variants.keys())))
            form.fields['variante'].choices = current_variants.items()
        else:
            LOGGER.debug("No hay variantes")
            form.fields['variante'].choices = current_variants.items()
            form.fields['variante'].widget.attrs['disabled'] = True
    elif current_variants['status'] == 'error':
        del current_variants['status']
        LOGGER.error("Al obtener variantes de Elasticsearch")
        messages.error(request, "Error de conexión a servidores :(")
    return render(request, "index.html",
                  {'form': form, 'total_variants': len(current_variants)})


def ayuda(request):
    """**Muestra la página de ayuda**

    Vista encargada de mostrar la sección de ayuda con las operaciones
    soportadas, como realizar busquedas y recomendaciones generales.

    :param request: Objeto ``HttpRequets`` para pasar el estado de la
                    app a través del sistema
    :type: ``HttpRequest``
    :return: Vista de ayuda
    """
    LOGGER.info("Entrando a ayuda")
    return render(request, "help.html")


def links(request):
    """**Muestra la página de enlaces de interés**

    Vista encargada de mostrar la sección de ligas de interés con la página de
    Elotl, el blog de Elotl y el diccionario del otomi


    :param request: Objeto ``HttpRequets`` para pasar el estado de
                    la app a través del sistema
    :type: ``HttpRequest``
    :return: Vista de enlaces de interés
    """
    LOGGER.info("Entrando a links")
    return render(request, "links.html")


def about(request):
    """**Muestra la página acerca del corpus**

    Vista encargada de mostrar la sección de acerca del corpus motivación del
    corpus y descripción general de la comunidad Elotl. Además, muestra la
    información actual del corpus como número de documentos, parrafos por
    documentos y pdfs asociados.

    :param request: Objeto ``HttpRequets`` para pasar el estado de la app a
                    través del sistema
    :type: ``HttpRequest``
    :return: Vista de acerca del corpus
    """
    LOGGER.info("Entrando a about")
    total, docs = get_corpus_info()
    try:
        repo = Repo('.')
        git = repo.git
        branches = git.branch().split("\n")
        current_branch = [branch for branch in branches if "*" in branch]
        current_branch = current_branch[0].strip("*").strip(" ")
        commits = list(repo.iter_commits(current_branch))
        last_commit = commits[0].hexsha
    except exc.InvalidGitRepositoryError:
        LOGGER.error("No se encontró repositorio de git")
        last_commit = ""
    return render(request, "about.html",
                  {"total": total, "docs": docs, "commit": last_commit})

# === Participantes ===


def participants(request):
    """**Muestra la página de participantes**

    Vista encargada de mostrar la sección de participantes con los nombres de
    los participantes y ligas de contacto con la comunidad Elotl

    :param request: Objeto ``HttpRequets`` para pasar el estado de la app a
                    través del sistema
    :type: ``HttpRequest``
    :return: Vista de participantes
    """
    LOGGER.info("Entrando a participants")
    return render(request, "participants.html")

# === Visor PDF ===


def pdf_view(request, file_name):
    """**Muestra archivos PDF con base en el nombre**

    :param request: Objeto ``HttpRequets`` para pasar el estado de la app a
                    través del sistema
    :type: ``HttpRequest``
    :param file_name: Nombre del ``PDF`` a mostrar
    :type: str
    :return: Archivo ``PDF`` para ser visto en el navegador
    """
    try:
        path = settings.BASE_DIR + settings.MEDIA_ROOT + file_name
        return FileResponse(open(path, 'rb'), content_type='application/pdf')
    except FileNotFoundError:
        path = settings.BASE_DIR + settings.MEDIA_ROOT + file_name
        LOGGER.error("No se encontro el PDF en " + path)
        raise Http404()
