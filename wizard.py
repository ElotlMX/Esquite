#!env/bin/python
import os
import secrets
import sys
import json
import yaml
import click
import elasticsearch
from pprint import pprint
from elasticsearch import Elasticsearch
from esquite.helpers import set_minimal_env


def set_project_info(config):
    """Escribe información general del proyecto

    Escribe en el diccionario de configuraciones el nombre de la
    organización, nombre del proyecto la primera y segunda lengua
    del corpus paralelo

    :param config: Diccionario con la configuración
    :type: dict
    :return: Diccionario de configuraciones con información del
             proyecto
    :rtype: dict
    """
    # Redes por defecto
    social = ["site", "blog", "email", "facebook", "twitter", "github"]
    config["ORG_NAME"] = input("\t * Nombre de la organización>> ").upper()
    config["NAME"] = input("\t * Nombre del proyecto>> ").upper()
    config["L1"] = input("\t * Primera lengua del corpus (l1)>> ").title()
    config["L2"] = input("\t * Segunda lengua del corpus (l2)>> ").title()
    # Colaboradoras vacio por defecto
    config["COLABS"] = []
    config["LINKS"] = {"social": {k: "" for k in social}, "corpora": dict()}
    config["META_DESC"] = input("\t * Descripción (etiqueta meta html): ")
    return config


def set_url(protocol="http", ip="localhost", port="9200"):
    """Contruye una URL válida para el archivo de configuración

    Dado el protocolo, la ip y el puerto contruye una URL válida para
    el archivo de configuración. Si las variables no fueron dadas por
    la usuaria utiliza la URL por defecto ``http://localhost:9200/``

    :param protocol: Protocolo que debe ser ``HTTP`` o ``HTTPS``
    :type: str
    :param ip: Nombre o ip del server de Elasticsearch
    :type: str
    :param port: Puerto del server Elasticsearch
    :type: str
    :return: URL válida para el proyecto
    :rtype: str
    """
    if protocol:
        url = f"{protocol}://"
    else:
        url = "http://"

    if ip:
        url += f"{ip}:"
    else:
        url += "localhost:"

    if port:
        url += f"{port}/"
    else:
        url += "9200/"
    return url


def set_services(config):
    """Escribe información de los servivios

    Escribe en el diccionario de configuraciones el nombre del índice
    y la url (ip y puerto) del servidor elasticsearch.

    :param config: Diccionario con la configuración
    :type: dict
    :return: Diccionario de configuraciones con información del
             de los servicios
    :rtype: dict
    """
    config["INDEX"] = input("\t * Índice de Elasticsearch[default]>> ") or "default"
    protocol = input("\t * Protocolo HTTP o HTTPS [http]>>")
    ip = input("\t * Nombre o IP del servidor de Elasticsearch [localhost]>>")
    port = input("\t * Puerto del servidor de Elasticsearch [9200]>>")
    config["URL"] = set_url(protocol, ip, port)
    index_flag = input("\t  Deseas crear el índice  [Y/n]>>")
    if index_flag == "y" or index_flag == "Y" or index_flag == "":
        create_index(config)
    else:
        print(f"\t⚙ Se Omitie la creación del indice {config['INDEX']} ⚙ ")
    return config


def create_index(config):
    """Crea un índice de Elasticsearch con la configuración por defecto"""
    es_client = Elasticsearch([config["URL"]])
    with open("elastic-config.json", "r", encoding="utf-8") as json_file:
        es_config = json.loads(json_file.read())
    print("\t⚙ Creando el índice con configuraciones por defecto ⚙")
    try:
        es_client.indices.create(index=config["INDEX"], body=es_config)
    except elasticsearch.exceptions.ConnectionError:
        print("[ERROR]: No se pudo conectar a la instancia de Elasticsearch :(")
        print("¿Instalaste elasticsearch?")
        print(
            "Guia de instalación: https://www.elastic.co/guide/en/elasticsearch/reference/7.9/install-elasticsearch.html"
        )
        sys.exit(1)
    except elasticsearch.exceptions.RequestError as e:
        print(f"[ERROR]: No se pudo crear el índice {config['INDEX']}")
        print(f"[REASON]: {e.error} [STATUS_CODE]: {e.status_code}")
        print("Intentalo de nuevo cambiando el nombre del índice")
        sys.exit(1)
    print("\t⚙ Creado ⚙")


def set_colors(config):
    """Escribe los colores del proyecto

    Escribe en el diccionario de configuraciones el color primario,
    secundario, color de los textos y color de contraste de los textos

    :param config: Diccionario con la configuración
    :type: dict
    :return: Diccionario de configuraciones con los colores del
             proyecto
    :rtype: dict
    """
    primary = "#fbda65"
    primary_hover = "#fdecb2"
    secondary = "#06a594"
    secondary_hover = "#69c9be"
    secondary_active = "#048476"
    text_color = "#000000"
    text_color_alt = "#ffffff"
    text_fields = {
        "button": text_color_alt,
        "btnhover": primary,
        "form": text_color,
        "bold": secondary,
        "highlight": secondary_active,
        "nav": secondary,
        "navhover": secondary_hover,
        "navactive": secondary_active,
        "result": text_color,
        "footer": text_color,
        "links": secondary,
        "hoverlinks": secondary_hover,
    }
    background_fields = {
        "form": primary_hover,
        "button": secondary,
        "btnhover": secondary_hover,
        "nav": primary,
        "footer": text_color_alt,
        "highlight": primary_hover,
    }
    border_fields = {"button": secondary, "input": secondary}
    config["COLORS"] = {
        "text": text_fields,
        "background": background_fields,
        "border": border_fields,
    }
    return config


def api_limits(config):
    """Establece valores de limites para la API

    Se añaden límites para el consumo de la API incluyendo número de
    request por hora y día, resultados máximos devueltos para una
    consulta y el número de proxies en el server.

    :param config: Diccionario con la configuración
    :type: dict
    :return: Configuraciones con los límites de la API
    :rtype: dict
    """
    config["API"] = {}
    # Limites de los request por dia y hora
    throttles = {
        "sustain_anon": "50/day",
        "burst_anon": "20/hour",
        "sustain_user": "200/day",
        "burst_user": "50/hour",
    }
    # Limite de los resultados devuelve la API
    limit_results = {"anon": 10, "user": 100}
    # Número de proxies en el server
    config["API"]["num_proxies"] = 0
    config["API"]["limit_results"] = limit_results
    config["API"]["throttles"] = throttles
    return config


def create_user_scheme(base_dir):
    user_templates_dir = os.path.join(base_dir, "templates/user")
    user_static_dir = os.path.join(base_dir, "static/user")
    # Creating user templates dir if not exists
    if not os.path.isdir(user_templates_dir):
        os.mkdir(user_templates_dir)
    # Creating user statics dirs if not exists
    if not os.path.isdir(user_static_dir):
        os.mkdir(user_static_dir)
        os.mkdir(os.path.join(user_static_dir, "js"))
        os.mkdir(os.path.join(user_static_dir, "css"))
        os.mkdir(os.path.join(user_static_dir, "img"))
    # User templates
    about_file = os.path.join(user_templates_dir, "about-user.html")
    links_file = os.path.join(user_templates_dir, "links-user.html")
    help_file = os.path.join(user_templates_dir, "help-user.html")
    colabs_file = os.path.join(user_templates_dir, "participants-user.html")
    try:
        # Try to create templates
        print("\t# Creando templates HTML de usuariæ")
        with open(about_file, "w+") as about_f:
            default_about_string = """
      <p>Este corpus <b>paralelo</b> permite búsquedas de palabras o frases
      dentro de una colección de documentos bilingües digitalizados
      (traducciones).</p>
      <p>El sistema desplegará aquel conjunto de fragmentos/oraciones que
      contienen la palabra buscada en la lengua seleccionada, así como las
      oraciones paralelas asociadas en la otra lengua, es decir, sus
      traducciones.</p>
      <p>Este tipo de sistemas son útiles para estudiosos, aprendices y
      hablantes de la lengua que quieran observar cómo se traduce cierta
      palabra o frase dependiendo del contexto y de la fuente.</p>
            """
            about_f.write(default_about_string)
        open(links_file, "a").close()
        open(help_file, "a").close()
        open(colabs_file, "a").close()
    except FileExistsError:
        print("\t[WARN] No se pueden crear archivos. Parece que ya existen")
    except PermissionError:
        print("\t[ERROR] No se permite crear archivos en f{user_templates_dir}")


@click.command()
@click.option(
    "-q",
    "--quick",
    is_flag=True,
    help="Lanza el configurador en modo rápido (configuraciones por \
                    defecto)",
)
def main(quick):
    """Asistente de configuración de esquite wizard 🧙

    Este *script* se encarga de asistir a la usuaria para generar el archivo
    `env.yaml` que contiene las configuraciones generales del framework.
    El archivo mencionado es **necesario** para que el proyecto funcione
    correctamente.
    """
    click.secho("Asistente de configuración del backend 🧙\n", fg="green")
    # Configuraciones comúnes
    # Creando directorios de usuariæ
    base_dir = os.path.dirname(os.path.abspath(__file__))
    create_user_scheme(base_dir)
    # Generando Token Secreto del proyecto
    token = secrets.token_urlsafe(50)
    # Si se indica el modo interactivo
    if not quick:
        click.echo("# Configuraciones Generales (1/3)")
        config = dict()
        config = set_project_info(config)
        config["SECRET_KEY"] = token
        # Dejando por defecto el modo Debug Encendido
        config["DEBUG"] = "True"
        click.echo("# Configuración de ELASTICSEARCH (2/3)")
        config = set_services(config)
        # Teclas del teclado
        teclas = "test"
        config["KEYBOARD"] = list(teclas)
        click.echo("# Colores del proyecto (HEXADECIMALES) (3/3)")
        config = set_colors(config)
        # Configurando limites para la API
        config = api_limits(config)
    else:
        # Configuración default
        config = set_minimal_env(token)
    click.echo("# Generando archivo para la configuración:")
    click.secho("⚙" * 50, fg="yellow")
    pprint(config, indent=2, width=80)
    click.secho("⚙" * 50, fg="yellow")
    with open("env.yaml", "w") as conf_file:
        yaml.dump(config, conf_file)
    click.echo("# Terminado :)")


if __name__ == "__main__":
    main()
