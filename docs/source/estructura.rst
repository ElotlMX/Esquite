.. _estructura:

Estructura del proyecto
=======================

Esta sección está pensada para desarrolladoras y personas que desean
entender como está estructurado el proyecto para contribuir con
nuevo código o agregando características. 

General
~~~~~~~

El proyecto esta desarrollado en ``django`` y por tanto sigue una
estructura específica. A continuación se explicará la estructura del
proyecto haciendo énfasis en la descripción general de los módulos que
lo componen.

::

   Esquite                    # Carpeta raíz
   │   ├── corpus_admin/      # Modulo de administración de archivos
   │   ├── env/               # Entorno virtual para python
   │   ├── media/             # Archivos PDFs
   │   ├── searcher/          # Modulo de búsqueda
   │   ├── static/            # Archivos estáticos (css, js, img, ...)
   │   ├── templates/         # Vistas en .html
   │   ├── esquite/           # Modulo principal del proyecto
   │   ├── docs/              # Carpeta que contiene la documentación
   │   ├── api/               # Modulo de la api 
   │   ├── db.sqlite3         # Archivo para bases de datos
   │   ├── manage.py          # Command-line utility de django
   │   ├── __pycache__
   │   ├── README.md          # Archivo que describe el proyecto
   │   ├── requeriments.txt   # Descripción de las dependencias del proyecto
   │   └── wizard.py          # Asistente de instalación del proyecto

``esquite``
~~~~~~~~~~~

::

   esquite
   ├── __init__.py
   ├── __pycache__/
   ├── settings.py             # Configuraciones globales
   ├── urls.py                 # URLs generales
   ├── views.py                # Comportamiento de las vistas
   ├── context_processors.py   # Funciones para variables globales
   └── wsgi.py                 # Configuraciones para servidor web


El modulo ``esquite`` contiene la base del proyecto. En este modulo se
puede gestionar la **configuración global** del proyecto. También, las
**urls** generales, el comportamiento de la página de inicio y la forma
en que se despliegan los **pdfs**.

``searcher``
~~~~~~~~~~~~

::

   searcher
   ├── admin.py
   ├── apps.py
   ├── forms.py           # Formulario de búsqueda construido por django
   ├── helpers.py         # Funciones utilitarias para tratamiento de los datos
   ├── __init__.py
   ├── migrations/
   ├── models.py
   ├── __pycache__/
   ├── tests.py
   ├── urls.py            # Configuración de URLs para el modulo de búsqueda
   └── views.py           # Comportamiendo de las vistas y manejo de consultas

En el modulo ``searcher`` se encuentra el funcionamiento de las vistas
de búsqueda y manejo de las *queries* enviadas a ``elasticsearch``. También,
se pueden modificar las URLs del módulo ``searcher`` que comprenden todas
las disponibles en el navbar (ayuda, links, about, participantes). De
forma programática se genera el formulario de búsqueda. Este puede
modificarse en ``forms.py``. 

``corpus_admin``
~~~~~~~~~~~~~~~~

::

   corpus_admin
   ├── admin.py
   ├── apps.py
   ├── forms.py     # Formularios para agregar, editar o modificar el PDF de un documento
   ├── helpers.py   # Funciones utilitarias
   ├── __init__.py
   ├── migrations/
   ├── models.py
   ├── __pycache__/
   ├── tests.py
   ├── urls.py      # Configuración de URLs del manejo de documentos
   └── views.py     # Comportamiento de las vistas, carga de documentos, edición y validaciones

El modulo ``corpus_admin`` se encarga de recibir, validar, cargar,
editar y eliminar los documentos. Todo cambio se verá reflejado en el
API de ``elasticsearch``. Similar a ``searcher`` los formularios son
creados dinámicamente y se pueden editar en ``forms.py``. El archivo
``views.py`` es el que se encarga de la validación y subida de cualquier
cambio en los documentos. Algunas funciones toman los parámetros de las URLs.
La definición de los parámetros validos se puede configurar en ``urls.py``
así como las rutas del modulo.

``templates``
~~~~~~~~~~~~~

::

   templates
   ├── about.html
   ├── base.html
   ├── corpus-admin/
   │   ├── add-rows.html
   │   ├── doc-edit.html
   │   ├── doc-preview.html
   │   ├── docs-list.html
   │   └── new-doc.html
   ├── help.html
   ├── index.html
   ├── links.html
   ├── participants.html
   ├── searcher/
   │   └── searcher.html
   └── user/
        ├── about-user.html
        ├── help-user.html
        ├── links-user.html
        └── participants-user.html

En esta carpeta se encuentran las vistas ``.html`` que son llamadas por
los archivos ``views.py`` de los diferentes módulos. Por convención la
carpeta es llamada ``templates``. Se hace uso del motor de templates de
``django``. Más información del motor en la
`documentación <https://docs.djangoproject.com/en/2.2/topics/templates/#the-django-template-language>`__.
Además, se hace uso del *template inheritance* por lo que los elementos
comunes (navbar, banner, footer, etc) se encuentran en el archivo
``base.html`` y de ahí se extienden a las diferentes vistas. Igualmente,
el funcionamiento detallado de esta herramienta se puede encontrar en la
`documentación <https://docs.djangoproject.com/en/2.2/ref/templates/language/#template-inheritance>`__.
Por último la carpeta ``user`` contiene fragmentos ``.html`` que 
brindan la posibilidad a las usuarias incrustar partes personalizadas
en las vistas creadas.

``static``
~~~~~~~~~~

::

   static
   ├── css           # Estilos
   ├── data-tables   # Biblioteca para tablas y exportación de datos
   ├── img           # Imágenes del proyecto
   ├── js            # Scripts de bibliotecas
   ├── localisation  # Archivos de idiomas paralas tablas
   └── fork-awesome  # Iconos decorativos del proyecto como los botones

Carpeta que contiene los archivos estáticos del proyecto como estilos,
*scripts*, imágenes, iconos y bibliotecas utilizadas. Muchos de los
estilos se encuentran en ``css/main.css``. Para las tablas se utiliza la
biblioteca `DataTables <https://datatables.net/>`__ y para las
alertas `select2 <https://select2.org/>`__.
