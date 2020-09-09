# Esquite: framework para administrar corpus paralelos 🌽

[![Documentation Status](https://readthedocs.org/projects/esquite/badge/?version=latest)](https://esquite.readthedocs.io/es/latest/?badge=latest)
[![License](https://img.shields.io/github/license/ElotlMX/Esquite?label=Licencia&style=flat)](https://github.com/ElotlMX/Esquite/blob/master/LICENSE)

## Acerca de Esquite

Esquite es un *framework* está destinado para las personas que poseen corpus
paralelos (textos bilingües) y deseen generar un sistema web que les permita
subir estos documentos, administrarlos y realizar búsquedas de palabras
y frases en las dos lenguas.

### Características

* Realizar búsquedas avanzadas atreves de tus corpus paralelos gracias al motor
	de [*Elasticsearch*](https://www.elastic.co/es/)
* Gestionar tus documento por medio de su administrador de corpus
* Personalización de la interfaz web
	* Colores
	* Teclado con caracteres especiales (útil para lenguas minorizadas)
	* Agregar información personalizada a las vistas: **Ayuda**, **Acerca del Corpus**,
		etc.
* Nuevas características en desarrollo


### Ejemplo: [Tsunkua Corpus Paralelo Español-Otomí](https://tsunkua.elotl.mx/)

<p align="center">
	<img src="https://elotl.mx/wp-content/uploads/2020/07/tsunkua.png" width="40%" height="40%" />
	<img src="https://elotl.mx/wp-content/uploads/2020/07/export_csv.png" width="52%" height="52%" />
</p>

## Contacto

¿Eres hablante/estudioso de una lengua minorizada y te gustaría poner tu corpus
paralelo en línea? Contactamos: *contacto at elotl.mx*

## Documentación

Para una [guía de instalación](https://esquite.readthedocs.io/es/latest/install.html)
completa, [tutoriales](https://esquite.readthedocs.io/es/latest/tutorials.html)
y estructura del proyecto puedes revisar nuestra
[documentación](https://esquite.readthedocs.io/es/latest/).

## Dependencias

* `git`
* [Elasticsearch 7.6](https://www.elastic.co/guide/en/elasticsearch/reference/7.6/getting-started-install.html) o mayor
* `python3.6` o mayor
	* `pip`
	* Opcional: `virtualenv`: [Guía de instalación virtualenv](https://virtualenv.pypa.io/en/latest/installation.html)

## Instalación en servidor

1. Instalar y correr `elasticsearch`

	**Nota**: Puedes consultar la página oficial de 
	[Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
	para completar este paso dependiendo de tu Sistema Operativo

2. Clona este repositorio

	```shell
	$ git clone https://github.com/ElotlMX/Esquite
	```

3. Preparación del entorno

	Entrar a la carpeta del proyecto, crea un entorno virtual de `python` con
	`virtualenv` y activarlo

	```shell
	$ cd Esquite
	$ virtualenv env -p /usr/bin/python3
	$ source env/bin/activate
	```

4. Instalar las dependencias

	```shell
	(env)$ pip install -r requirements.txt
	```

5. Iniciar el asistente de instalación e ingresar los datos que piden

	```shell
	(env)$ python wizard.py
	```

	**Nota**: El asistente menciona que debemos tener un índice de `elasticsearh`
	previamente creado. Para crear dicho índice puede ejecutar el siguiente
	comando. 

	```shell
	$ curl -X PUT -H "Content-Type: application/json" -d @elastic-config.json localhost:9200/<nombre-de-tu-indice>
	```

	Donde dice `<nombre-de-tu-indice>` deberás poner el nombre que desees
	y ese será el nombre del índice para poner en el asistente de instalación.


6. Correr `django` en segundo plano

	```shell
	(env)$ python manage.py runserver 0.0.0.0:3000 &
	```

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

El modulo `esquite` contiene la base del proyecto. En este modulo se puede
gestionar la **configuración global** del proyecto. Tambien, las **urls**
generales y el comportamiento de la página de inicio y la forma en que se
despliegan los **pdfs**.

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
`forms.py`. Por último, el archivo `request_base.json` es el esqueleto de la
*query* que será enviada a la API de elasticsearch, se modifica al recibir una
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

El modulo `corpus_admin` se encarga de recibir, validar, cargar, editar
y eliminar los documentos. Todo cambio se verá reflejado en el API de
`elasticsearch`. Similar a `searcher` los formularios son creados dinámica mente
y se pueden editar en `forms.py`. El archivo `views.py` es el que se encarga de
la validación y subida de cualquier cambio. Algunas funciones toman los
parámetros de las URLs. La definición de los parámetros validos se puede
configurar en `urls.py` así como las rutas del modulo.

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

En esta carpeta se encuentran las vistas `.html` que son llamadas por los
archivos `views.py` de los diferentes módulos. Por convención la carpeta es
llamada `templates`. Se hace uso del motor de templates de `django`. Más
información del motor en la
[documentación](https://docs.djangoproject.com/en/2.2/topics/templates/#the-django-template-language).
Además, se hace uso del *template iheritance* por lo que los elementos comunes
(navbar, banner, footer, etc) se encuentran en el archivo `base.html` y de ahí
se extienden a las diferentes vistas. Igualmente, el funcionamiento detallado
de esta herramienta se puede encontrar en la
[documentación](https://docs.djangoproject.com/en/2.2/ref/templates/language/#template-inheritance)

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

Carpeta que contiene los archivos estáticos del proyecto como estilos, scripts,
imágenes, iconos y bibliotecas utilizadas. Muchos de los estilos se encuentran
en `css/main.css`. Para las tablas se utiliza la biblioteca
[`DataTables`](https://datatables.net/) y para las alertas
[`select2`](https://select2.org/).

