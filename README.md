# Esquite: framework to manage parallel corpus 🌽

[![Documentation Status](https://readthedocs.org/projects/esquite/badge/?version=latest)](https://esquite.readthedocs.io/es/latest/?badge=latest)
[![License](https://img.shields.io/github/license/ElotlMX/Esquite?label=Licencia&style=flat)](https://github.com/ElotlMX/Esquite/blob/master/LICENSE)
[![README ES](https://img.shields.io/badge/README-Espa%C3%B1ol-informational)](https://github.com/ElotlMX/Esquite/blob/master/README_ES.md)

## About Esquite

Esquite is a *framework* that is intended for people who have parallel corpus
(bilingual texts) and wish generate a web system that allows to upload these
documents, manage them and make queries of words and phrases in both languages.

---

Esquite es un *framework* está destinado para las personas que poseen corpus
paralelos (textos bilingües) y deseen generar un sistema web que les permita
subir estos documentos, administrarlos y realizar búsquedas de palabras
y frases en las dos lenguas.

### Features

* Make advance queries through your parallel corpus thanks to the search engine
[*Elasticsearch*](https://www.elastic.co/es/)
* Manage your documents through the corpus administrator
* Customization of the Web Client
    * Colors
    * Keyboard with special characters (useful for minoritised languages)
    * Add custom information to the views: **help**, **about corpus**,
      **links**, **etc**.
* New features in development

---

* Realizar búsquedas avanzadas atreves de tus corpus paralelos gracias al motor
	de búsquedas de [*Elasticsearch*](https://www.elastic.co/es/)
* Gestionar tus documento por medio de su administrador de corpus
* Personalización de la interfaz web
	* Colores
	* Teclado con caracteres especiales (útil para lenguas minorizadas)
	* Agregar información personalizada a las vistas: **Ayuda**, **Acerca del Corpus**,
		**Links**, etc.
* Nuevas características en desarrollo


### Example: [Tsunkua Corpus Paralelo Español-Otomí](https://tsunkua.elotl.mx/)

<p align="center">
	<img src="https://elotl.mx/wp-content/uploads/2020/07/tsunkua.png" width="40%" height="40%" />
	<img src="https://elotl.mx/wp-content/uploads/2020/07/export_csv.png" width="52%" height="52%" />
</p>

## Contact

Are you a speaker/studious of a minoritised language and would you like to put
your parallel corpus online? Contact us: *contacto at elotl.mx*

---

¿Eres hablante/estudioso de una lengua minorizada y te gustaría poner tu corpus
paralelo en línea? Contactamos: *contacto at elotl.mx*

### Collaborators

* **Leadership:** Xim ([@XimGuitierrez](https://twitter.com/XimGutierrez)) - xim at unam.mx
* **Mantainer:** Diego B. ([@umoqnier](https://twitter.com/umoqnier)) - *diegobarriga at protonmail.com*
* **DevOps**: Javier ([@jusafing](https://twitter.com/jusafing)) -

### Community

* Twitter: [@elotlmx](https://twitter.com/elotlmx)
* Site: [https://elotl.mx/](https://elotl.mx)
* Email: *contacto at elotl.mx*

## Docs

For a full [instalation
guide](https://esquite.readthedocs.io/es/latest/install.html),
[tutorials](https://esquite.readthedocs.io/es/latest/tutorials.html) and project
structure you can check our
[documentation](https://esquite.readthedocs.io/es/latest/).


---


Para una [guía de instalación](https://esquite.readthedocs.io/es/latest/install.html)
completa, [tutoriales](https://esquite.readthedocs.io/es/latest/tutorials.html)
y estructura del proyecto puedes revisar nuestra
[documentación](https://esquite.readthedocs.io/es/latest/).

### Dependencies

* `git`
* [Elasticsearch
  7.6](https://www.elastic.co/guide/en/elasticsearch/reference/7.6/getting-started-install.html)
  or higher
* `python3.6` or higher
	* `pip`
	* Optional: `virtualenv`: [virtualenv instalation guide](https://virtualenv.pypa.io/en/latest/installation.html)

### Installation

1. Install and run `elasticsearch`

    **Note**: You can check the official page of
	[Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
    to complete this step depending on your Operating System

---

1. Instalar y correr `elasticsearch`

	**Nota**: Puedes consultar la página oficial de
	[Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
	para completar este paso dependiendo de tu Sistema Operativo

2. Clone this repo

	```shell
	$ git clone https://github.com/ElotlMX/Esquite
	```


---

2. Clona este repositorio

	```shell
	$ git clone https://github.com/ElotlMX/Esquite
	```

3. Environment setting

    Change to the directory's project, make a virtual environment of `python`
    with `virtualenv` and activate

	```shell
	$ cd Esquite
	$ virtualenv env -p /usr/bin/python3
	$ source env/bin/activate
	```

---


3. Preparación del entorno

	Entrar a la carpeta del proyecto, crea un entorno virtual de `python` con
	`virtualenv` y activarlo

	```shell
	$ cd Esquite
	$ virtualenv env -p /usr/bin/python3
	$ source env/bin/activate
	```

4. Install dependencies

	```shell
	(env)$ pip install -r requirements.txt
	```

---


4. Instalar las dependencias

	```shell
	(env)$ pip install -r requirements.txt
	```

5. Launch the installation wizard and enter the data requested

	```shell
	(env)$ python wizard.py
	```

    **Note**: The wizard displays that we need an `elasticsearch` index previously
    created. To create this index you can run the `curl` command below

	```shell
	$ curl -X PUT -H "Content-Type: application/json" -d @elastic-config.json localhost:9200/<nombre-de-tu-indice>
	```

    Where you find `<your-index-name>` you should set the name you would and
    this will be the name of the index to be entered into the installation wizard.

---


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

6. Apply `django` migrations

	```shell
	(env)$ python manage.py migrate
	```

---

6. Aplicar migraciones de `django`

	```shell
	(env)$ python manage.py migrate
	```

6. Run `django` in background

	```shell
	(env)$ python manage.py runserver 0.0.0.0:8000 &
	```

---

6. Correr `django` en segundo plano

	```shell
	(env)$ python manage.py runserver 0.0.0.0:8000 &
	```

