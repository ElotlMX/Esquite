"""
Configuración de WSGI para el proyecto.

Para mas información consulta la documentación de django `aqui
<https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/>`
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elotl.settings')

application = get_wsgi_application()
