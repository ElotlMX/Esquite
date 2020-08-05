# Esquite: framework para administrar corpus paralelos

[![Documentation Status](https://readthedocs.org/projects/esquite/badge/?version=latest)](https://esquite.readthedocs.io/es/latest/?badge=latest)

Este framework está destinado para las personas que poseen corpus paralelos (textos bilingües) y deseen generar un sistema web que les permita subir estos documentos, administrarlos y realizar búsquedas de palabras y frases en las dos lenguas.


Ejemplo: [Tsunkua Corpus Paralelo Español-Otomí](https://tsunkua.elotl.mx/)

## Documentación

Puedes revisar nuestra [documentación](https://esquite.readthedocs.io/es/latest/) para más información.

## Dependencias

* [Elasticsearch 7.6](https://www.elastic.co/guide/en/elasticsearch/reference/7.6/getting-started-install.html)
* `python3.6` o mayor
* `pip`
* `virtualenv`
    * [Guía de instalación virtualenv](https://virtualenv.pypa.io/en/stable/installation/)

## Instalación en servidor

1. Clona este repositorio
2. Crea un entorno virtual de `python`
	* `$ virtualenv env -p /usr/bin/python3`
3. Activar el entorno
	* `$ source env/bin/activate`
4. Instalar las dependencias
	*	`(env)$ pip install -r requeriments.txt`
5. Iniciar el asistente de instalación e ingresar los datos que piden
  * `(env)$ python wizard.py`
6. Correr django en segundo plano
  * `(env)$ python manage.py runserver 0.0.0.0:3000 &`

## Estructura general

El proyecto esta desarrollado en `django` y por tanto sigue una estructura
específica. A continuación se explicará la estructura del proyecto haciendo
énfasis en la descripción general de los módulos que lo componen.


```
esquite-backend            # Carpeta raíz
│   ├── db.sqlite3         # Archivo para bases de datos (No se utiliza)
│   ├── corpus_admin/      # Modulo de administración de archivos
│   ├── env/               # Entorno virtual para python
│   ├── manage.py          # Command-line utility de django
│   ├── media/             # Archivos PDFs
│   ├── __pycache__
│   ├── README.md          # Archivo que describe el proyecto
│   ├── requeriments.txt   # Descripción de las dependencias del proyecto
│   ├── searcher/          # Modulo de búsqueda
│   ├── static/            # Archivos estáticos (css, js, img, ...)
│   ├── templates/         # Vistas en .html
│   ├── esquite/           # Modulo principal del proyecto
│   └── wizard.py          # Asistente de instalación del proyecto
```

### `esquite`

```
esquite
├── __init__.py
├── __pycache__/
├── settings.py  # Configuraciones globales
├── urls.py      # URLs generales
├── views.py     # Comportamiento de las vistas
└── wsgi.py
```
El modulo `esquite` contiene la base del proyecto. En este modulo se puede gestionar la **configuración global** del proyecto. Tambien, las **urls** generales y el comportamiento de la página de inicio y la forma en que se despliegan los **pdfs**.

### `searcher`

```
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
```
En el modulo `searcher` se encuentra el funcionamiento de las vistas de
búsqueda y manejo de las queries enviadas a elasticsearch. Tambien, se
pueden modificar las URLs del módulo searcher que comprenden todas las
disponibles en el navbar (ayuda, links, about, participantes). De forma
programática se genera el formulario de búsqueda. Este puede modificarse en
`forms.py`. Por útlimo, el archivo `request_base.json` es el esqueleto de la
querie que será enviada a la API de elasticsearch, se modifica al recibir una
consulta `POST` en la vista `search` del archivo `views.py`.

### `corpus_admin`

```
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
├── urls.py      # Configuración de URLsdel manejo de documentos
└── views.py     # Comportamiento de las vistas, carga de documentos, edición y validaciones
```
El modulo `corpus_admin` se encarga de recibir, validar, cargar, editar y eliminar los documentos. Todo cambio se verá reflejado en el API de elasticsearch. Similar a `searcher` los formularios son creados dinámica mente y se pueden editar en `forms.py`. El archivo `views.py` es el que se encarga de la validación y subida de cualquier cambio. Algunas funciones toman los parámetros de las URLs. La definición de los parámetros validos se puede configurar en `urls.py` asi como las rutas del modulo.

### `templates`

```
templates
├── about.html
├── base.html
├── corpus-admin/
│   ├── add-rows.html
│   ├── doc-edit.html
│   ├── doc-preview.html
│   ├── docs-list.html
│   └── new-doc.html
├── help.html
├── index.html
├── links.html
├── participants.html
└── searcher/
    └── searcher.html
```
En esta carpeta se encuentran las vistas `.html` que son llamadas por los archivos `views.py` de los diferentes modulos. Por convención la carpeta es llamada `templates`. Se hace uso del motor de templates de `django`. Más información del motor en la [documentación](https://docs.djangoproject.com/en/2.2/topics/templates/#the-django-template-language). Además, se hace uso del *template iheritance* por lo que los elementos comúnes (navbar, banner, footer, etc) se encuentran en el archivo `base.html` y de ahí se extienden a las diferentes vistas. Igualmente, el funcionamiento detallado de esta herramienta se puede encontrar en la [documentación](https://docs.djangoproject.com/en/2.2/ref/templates/language/#template-inheritance)

### `static`

```
static
├── css           # Estilos
├── data-tables   # Biblioteca para tablas y exportación de datos
├── img           # Imágenes del proyecto
├── js            # Scripts de bibliotecas
├── localisation  # Archivos de idiomas paralas tablas
└── fork-awesome  # Iconos decorativos del proyecto como los botones
```
Carpeta que contiene los archivos estáticos del proyecto como estilos, scripts, imagenes, iconos y bibliotecas utilizadas. Muchos de los estilos se encuentran en `css/main.css`. Para las tablas se utiliza la biblioteca [`DataTables`](https://datatables.net/) y para las alertas [`select2`](https://select2.org/).

## Configuración del índice

Esta configuración es la utilizada actualmente en el índice de elasticsearch para hacer el preprocesamiento del español tomando en cuenta las *stopwords*

### Index Settings

```json
{
  "number_of_shards": 1,
  "analysis": {
      "filter": {
        "spanish_stop": {
          "type":       "stop",
          "stopwords":  "_none_"
        },
        "spanish_stemmer": {
          "type": "stemmer",
          "language": "light_spanish"
        }
      },
      "analyzer": {
        "rebuilt_spanish": {
          "tokenizer":  "standard",
          "filter": [
            "lowercase",
            "spanish_stop",
            "spanish_stemmer"
          ]
        }
      }
    }
}
```

### Mapping

```json
{
  "document_file": {
    "type": "keyword"
  },
  "document_id": {
    "type": "keyword"
  },
  "document_name": {
    "type": "keyword"
  },
  "lang_1": {
    "type": "text",
    "analyzer":"rebuilt_spanish"
  },
  "lang_2": {
    "type": "text"
  },
  "variante": {
    "type": "keyword"
  }
}
```

### Ingest Pipeline

```json
{
  "description": "Ingest pipeline created by file structure finder",
  "processors": []
}
  ```

## Contacto
¿Eres hablante/estudioso de una lengua minorizada y te gustaría poner tu corpus paralelo en línea?
Contáctanos: *contacto@elotl.mx*
