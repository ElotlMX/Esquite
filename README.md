# Esquite: framework to manage parallel corpus 🌽

[![Documentation Status](https://readthedocs.org/projects/esquite/badge/?version=latest)](https://esquite.readthedocs.io/es/latest/?badge=latest)
[![License](https://img.shields.io/github/license/ElotlMX/Esquite?label=Licencia&style=flat)](https://github.com/ElotlMX/Esquite/blob/master/LICENSE)
[![README ES](https://img.shields.io/badge/README-Espa%C3%B1ol-informational)](https://github.com/ElotlMX/Esquite/blob/master/README_ES.md)


## What is Esquite?

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

## Docs

For a full [installation guide](https://esquite.readthedocs.io/es/latest/install.html),
[tutorials](https://esquite.readthedocs.io/es/latest/tutorials.html) and project
structure you can check our [documentation](https://esquite.readthedocs.io/es/latest/).

## Dependencies

* `git`
* [Elasticsearch 7.6](https://www.elastic.co/guide/en/elasticsearch/reference/7.6/getting-started-install.html) or higher
* `python 3.12` or higher
* `uv`

## Installation

1. Install and run `elasticsearch`

> [!NOTE]
> Check the official page of
> [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html)
> to complete this step depending on your OS. Alternatively you can use
> [docker](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
> for easier installation.


2. [Install](https://docs.astral.sh/uv/getting-started/installation/) `uv` in
   your system

	```shell
    curl -LsSf https://astral.sh/uv/install.sh | sh
	```

3. Clone this repo

	```shell
	$ git clone https://github.com/ElotlMX/Esquite --depth=1
	```

4. Install dependencies

    Change to the directory's project and intall dependencies. Switch to
    project enviroment

	```shell
	$ cd Esquite
	$ uv sync --no-dev --no-group docs
    $ source .venv/bin/activate
	```

5. Launch the installation wizard and type the information requested

	```shell
	(venv)$ python wizard.py
	```

> [!TIP]
> The wizard automatically create an `elasticsearch` index.
> Alternatively you can run the `curl` command below to create an index
> manually before running the wizard.
> Default configs can be founded in the file `elastic-config.json`

	```shell
	$ curl -X PUT -H "Content-Type: application/json" -d @elastic-config.json localhost:9200/<index-name>
	```

6. Apply `django` migrations

	```shell
	(env)$ python manage.py migrate
	```

7. Run `django` in background

	```shell
	(env)$ python manage.py runserver 0.0.0.0:8000 &
	```

8. Go to your browser at `http://localhost:8000/` to see Esquite running :)

> [!NOTE]
> For an in detail deployment guide see please contact us

## Docker image alternative: `Esquite-Docker`

Alternatively, it is possible to use Esquite and deploy it in an easier way by
using our official Docker image.

Detailed documentation is available on:

- Esquite-Docker Github : https://github.com/ElotlMX/Esquite-docker
- Esquite-Docker Dockerhub : https://hub.docker.com/r/elotlmx/esquite

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

