import logging
import re
from django.conf import settings

LOGGER = logging.getLogger(__name__)

def keyboard(request):
    """**Configura variable de entorno para teclaod personalizado**
    """
    return {'KEYBOARD': settings.KEYBOARD}

def languages(request):
    """**Configura variables de entorno de las lenguas**"""
    return {'L1': settings.L1, 'L2': settings.L2}


def colors(request):
    """**Configura variables de entorno para los colores**"""
    return {'COLORS': settings.COLORS}


def project_info(request):
    """**Configura variables de entorno con información del proyecto**

    La información que se establece es *nombre*, *nombre de la organización*,
    *colaboradoras* y *redes sociales*. Las últimas dos son listas de python.
    """
    return {'PROJECT_NAME': settings.NAME, 'ORG_NAME': settings.ORG_NAME,
            'COLABS': settings.COLABS, 'SOCIAL': settings.SOCIAL}


def google_analytics(request):
    """**Configura variables de entorno de google analytics**"""
    return settings.GOOGLE_ANALYTICS


def user_templates(request):
    views = ["about", "help", "links", "participants"]
    regex = re.compile("[\w+\.\\n+\b+]$", re.MULTILINE)
    user_views = {}
    for view in views:
        path = f"{settings.BASE_DIR}/templates/user/{view}-user.html"
        try:
            with open(path, 'r') as html:
                html_view = html.read()
                html_view = regex.sub("<br>", html_view)
                html_view += "<br>"
        except FileNotFoundError:
            LOGGER.error("No se encontró el template de usuario", view)
            html_view = ""
        name = view.upper() + "_USER"
        user_views[name] = html_view
    return user_views
