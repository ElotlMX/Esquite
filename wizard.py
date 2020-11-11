#!env/bin/python
import secrets
import yaml
from pprint import pprint


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
    config['ORG_NAME'] = input("\t * Nombre de la organización>> ").upper()
    config['NAME'] = input("\t * Nombre del proyecto>> ").upper()
    config['L1'] = input("\t * Primera lengua del corpus (l1)>> ").title()
    config['L2'] = input("\t * Segunda lengua del corpus (l2)>> ").title()
    # Colaboradoras vacio por defecto
    config['COLABS'] = []
    config['SOCIAL'] = {k: "" for k in social}
    config['META_DESC'] = input("\t * Descripción del sitio (etiqueta meta de html): ")
    return config


def set_url(protocol="http", ip="localhost", port="9200"):
    """ Contruye una URL válida para el archivo de configuración

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
    y la url (ip y puerto) del servidor elasticsearch. Opcionalmente
    el token de Google Analytics.

    :param config: Diccionario con la configuración
    :type: dict
    :return: Diccionario de configuraciones con información del
             de los servicios
    :rtype: dict
    """
    notification = "\n🛑 El corpus requiere que exista un indice de\n" + \
                   "Elasticsearch con las configuraciones que se indican\n" + \
                   "en la documentación 🛑\n"
    print("⚙" * 55 + notification + "⚙" * 55)
    config['INDEX'] = input('\t * Índice de Elasticsearch>> ')
    protocol = input("\t * Protocolo HTTP o HTTPS [http]>>")
    ip = input("\t * Nombre o IP del servidor de Elasticsearch [localhost]>>")
    port = input("\t * Puerto del servidor de Elasticsearch [9200]>>")
    config['URL'] = set_url(protocol, ip, port)
    config['GOOGLE_ANALYTICS'] = input('\t * Token Google Analytics (OPCIONAL)>> ')
    return config


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
    config['COLORS'] = {"text": {}, "background": {}, "border": {}}
    background_color = input('\t * Color de fondo [#ffffff]>>') or "#ffffff"
    text_color = input('\t * Color de texto [#000000]>>') or "#000000"
    highlight_color = input('\t * Color de resaltado [#000000]>>') or "#000000"
    text_fields = {
        "highlight": highlight_color, "result": text_color, "nav": text_color,
        "form": text_color, "button": text_color, "hover": highlight_color
    }
    background_fields = {
        "nav": background_color, "form": background_color,
        "button": background_color, "hover": text_color
    }
    border_fields = {"button": text_color}
    config['COLORS']['text'] = text_fields
    config['COLORS']['background'] = background_fields
    config['COLORS']['border'] = border_fields
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
    config['API'] = {}
    # Limites de los request por dia y hora
    throttles = {'sustain_anon': '50/day', 'burst_anon': '20/hour',
                 'sustain_user': '200/day', 'burst_user': '50/hour'}
    # Limite de los resultados devuelve la API
    limit_results = {'anon': 10, 'user': 100}
    # Número de proxies en el server
    config['API']['num_proxies'] = 0
    config['API']['limit_results'] = limit_results
    config['API']['throttles'] = throttles
    return config



def main():
    """Función principal del asistente de configuración

    Genera token secreto del proyecto y escribe las configuraciones
    en el archivo ``env.yaml`` en la raíz del proyecto.
    """
    print("Asistente de configuración del backend 🧙\n")
    print("# Configuraciones Generales (1/3)")
    config = set_project_info({})
    # Generando Token Secreto
    config['SECRET_KEY'] = secrets.token_urlsafe(50)
    # Dejando por defecto el modo Debug Encendido
    config['DEBUG'] = 'True'
    print("# Configuracion de servicios (2/3)")
    config = set_services(config)
    # Vacio por defecto
    config['KEYBOARD'] = []
    print("# Colores del proyecto (HEXADECIMALES) (3/3)")
    config = set_colors(config)
    # Configurando limites para la API
    config = api_limits(config)
    print("# Generando archivo para la configuración:")
    print("⚙"*50)
    pprint(config)
    print("⚙"*50)
    with open("env.yaml", 'w') as conf_file:
        yaml.dump(config, conf_file)
    print("# Terminado :)")


if __name__ == "__main__":
    main()
