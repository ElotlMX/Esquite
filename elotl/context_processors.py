from django.conf import settings


def keyboard(request):
    """**Configura variable de entorno para teclaod personalizado**
    """
    return {'KEYBOARD': settings.KEYBOARD}

def languages(request):
    """**Configura variables de entorno de las lenguas**"""
    return {'LANG_1': settings.LANG_1, 'LANG_2': settings.LANG_2}


def colors(request):
    """**Configura variables de entorno para los colores**"""
    return {'PRIMARY_COLOR': settings.PRIMARY_COLOR,
            'SECONDARY_COLOR': settings.SECONDARY_COLOR,
            'TEXT_COLOR': settings.TEXT_COLOR, 'ALT_TEXT': settings.ALT_TEXT}


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
