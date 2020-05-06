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
    config['ORG_NAME'] = input("Nombre de la organización>> ").upper()
    config['NAME'] = input("Nombre del proyecto>> ").upper()
    config['LANG_1'] = input("Primera lengua del corpus (lang_1)>> ").title()
    config['LANG_2'] = input("Segunda lengua del corpus (lang_2)>> ").title()
    # Colaboradoras vacio por defecto
    config['COLABS'] = []
    config['SOCIAL'] = {k: "" for k in social}
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
    print("⚙" * 60 + notification + "⚙" * 60)
    config['INDEX'] = input('Índice de Elasticsearch>> ')
    protocol = input("Protocolo HTTP o HTTPS [http]>>")
    ip = input("Nombre o IP del servidor de Elasticsearch [localhost]>>")
    port = input("Puerto del servidor de Elasticsearch [9200]>>")
    config['URL'] = set_url(protocol, ip, port)
    config['GOOGLE_ANALYTICS'] = input('Token Google Analytics (OPCIONAL)>> ')
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
    primary_color = input('Primario [#ffffff]>>#') or "ffffff"
    secondary_color = input('Secundario [#000000]>>#') or "000000"
    r = compute_color(int(primary_color[:2], base=16))
    g = compute_color(int(primary_color[2:4], base=16))
    b = compute_color(int(primary_color[4:], base=16))
    config['PRIMARY_COLOR'] = '#' + primary_color
    config['SECONDARY_COLOR'] = '#' + secondary_color
    config['TEXT_COLOR'] = get_text_color(r, g, b)
    config['ALT_TEXT'] = "#000000" if config['TEXT_COLOR'][-1] == 'f' else '#ffffff'
    return config


def compute_color(c):
    """Convierte de sRGB a RGB líneal

    Se toma un color con su representación decimal y retorna el color en RGB
    líneal

    :param c: Color
    :type: int
    :return: Color en RGB líneal
    :rtype: float
    """
    # Referencia:
    # ``https://stackoverflow.com/questions/3942878/how-to-decide-font-color-in-white-or-black-depending-on-background-color/``
    c /= 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def get_text_color(r, g, b):
    """ Obtiene el color del texto

    Dada la luminocidad del color retorna el color del texto para que
    contraste con el color de fondo previamente configurado

    :param r: color rojo en RGB líneal
    :type: float
    :param g: color verde en RGB líneal
    :type: float
    :param b: color azul en RGB líneal
    :type: float
    :return: Cadena con color negro o blanco en hexadecimal
    :rtype: str
    """
    # Referencia:
    # ``https://www.w3.org/TR/WCAG20/#relativeluminancedef``
    luminosity = 0.2126 * r + 0.7152 * g + 0.0722 * b
    return "#000000" if luminosity > 0.179 else "#ffffff"


def main():
    """Función principal del asistente de configuración

    Genera token secreto del proyecto y escribe las configuraciones
    en el archivo ``env.yaml`` en la raíz del proyecto.
    """
    print("Asistente de configuración del backend 🧙\n\n")
    config = set_project_info({})
    print("Generando token secreto")
    config['SECRET_KEY'] = secrets.token_urlsafe(50)
    config['DEBUG'] = 'False'
    config = set_services(config)
    # Vacio por defecto
    config['KEYBOARD'] = []
    print("Colores del proyecto (HEXADECIMALES)")
    config = set_colors(config)
    print("Generando archivo para la configuración:")
    pprint(config)
    with open("env.yaml", 'w') as conf_file:
        yaml.dump(config, conf_file)
    print("Terminado :)")


if __name__ == "__main__":
    main()
