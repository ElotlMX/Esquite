# Esquite: framework to manage parallel corpus 🌽

[![Documentation Status](https://readthedocs.org/projects/esquite/badge/?version=latest)](https://esquite.readthedocs.io/es/latest/?badge=latest)
[![License](https://img.shields.io/github/license/ElotlMX/Esquite?label=Licencia&style=flat)](https://github.com/ElotlMX/Esquite/blob/master/LICENSE)
[![README ES](https://img.shields.io/badge/README-Espa%C3%B1ol-informational)](https://github.com/ElotlMX/Esquite/blob/master/README_ES.md)

## About Esquite

Esquite is a framework intended for people who have parallel corpus
(bilingual texts) and wish to get a web system that allows them to upload
documents, manage them and perform queries based on words and phrases in both
languages.

### Features

* Perform advanced queries in your parallel corpus thanks to the search engine
[*Elasticsearch*](https://www.elastic.co/es/)
* Manage your documents through the corpus administrator
* Customization of the Web Client
    * Colors
    * Keyboard with special characters (useful for non-english languages)
    * Add custom `html` information to the views: **help**, **about corpus**,
      **links**, **etc**.
* New features in development

### Example: [Tsunkua Corpus Paralelo Español-Otomí](https://tsunkua.elotl.mx/)

<p align="center">
	<img src="https://elotl.mx/wp-content/uploads/2020/07/tsunkua.png" width="40%" height="40%" />
	<img src="https://elotl.mx/wp-content/uploads/2020/07/export_csv.png" width="52%" height="52%" />
</p>

## Contact

Are you a speaker/researcher of a minority language and would like to upload
your parallel corpus? Contact us: *contacto at elotl.mx*

### Collaborators

* **Collaborator:** Xim ([@XimGutierrez](https://twitter.com/XimGutierrez)) - *xim at unam.mx*
* **Mantainer:** Diego B. ([@umoqnier](https://twitter.com/umoqnier)) - *diegobarriga at protonmail.com*
* **DevOps**: Javier ([@jusafing](https://twitter.com/jusafing)) - *jusafing at jusanet.org*

### Community

* Twitter: [@elotlmx](https://twitter.com/elotlmx)
* Site: [https://elotl.mx/](https://elotl.mx)
* Email: *contacto at elotl.mx*

## Docs

For a full [installation
guide](https://esquite.readthedocs.io/es/latest/install.html),
[tutorials](https://esquite.readthedocs.io/es/latest/tutorials.html) and project
structure you can check our
[documentation](https://esquite.readthedocs.io/es/latest/).

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

2. Clone this repo

	```shell
	$ git clone https://github.com/ElotlMX/Esquite
	```

3. Environment settings

    Change to the directory's project, make a virtual environment of `python`
    with `virtualenv` and activate

	```shell
	$ cd Esquite
	$ virtualenv env -p /usr/bin/python3
	$ source env/bin/activate
	```

4. Install dependencies

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

    Replace `<your-index-name>` with the index  name that  will  be used by
    installation wizard.

6. Apply `django` migrations

	```shell
	(env)$ python manage.py migrate
	```

7. Run `django` in background

	```shell
	(env)$ python manage.py runserver 0.0.0.0:8000 &
	```
