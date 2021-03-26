import secrets


def set_minimal_env(token="dummy-token"):
    """**Función que genera un diccionario con las configuraciones mínimas**
    :param token: Token secreto del proyecto
    :type: str
    :returns: Configuraciones mínimas del proyecto
    :rtype: dict
    """
    config = {
                'API': {
                    'limit_results': {'anon': 10, 'user': 100},
                    'num_proxies': 0,
                    'throttles': {
                        'burst_anon': '20/hour',
                        'burst_user': '50/hour',
                        'sustain_anon': '50/day',
                        'sustain_user': '200/day'
                    }
                },
                'COLABS': [],
                'COLORS': {
                    'background': {
                        'btnhover': '#69c9be',
                        'button': '#06a594',
                        'footer': '#ffffff',
                        'form': '#fdecb2',
                        'highlight': '#fdecb2',
                        'nav': '#fbda65'
                    },
                    'border': {'button': '#06a594', 'input': '#06a594'},
                    'text': {
                        'bold': '#06a594',
                        'btnhover': '#fbda65',
                        'button': '#ffffff',
                        'footer': '#000000',
                        'form': '#000000',
                        'highlight': '#048476',
                        'hoverlinks': '#69c9be',
                        'links': '#06a594',
                        'nav': '#06a594',
                        'navactive': '#048476',
                        'navhover': '#69c9be',
                        'result': '#000000'
                    }
                },
                'DEBUG': 'True',
                'GOOGLE_ANALYTICS': '',
                'INDEX': 'default',
                'KEYBOARD': ['k', 'e', 'y', 's'],
                'L1': 'L1',
                'L2': 'L2',
                'LINKS': {
                    'corpora': {},
                    'social': {
                        'blog': '',
                        'email': '',
                        'facebook': '',
                        'github': '',
                        'site': '',
                        'twitter': ''
                    }
                },
                'META_DESC': 'Framework de corpus paralelos Esquite',
                'NAME': 'ESQUITE',
                'ORG_NAME': 'ELOTLMX',
                'SECRET_KEY': f'{token}',
                'URL': 'http://localhost:9200/'
            }
    return config


def env_validator(env_configs):
    """**Función que valida que las configuraciones de entorno**
    :param env_configs: Configuraciones de entorno. Vienen del archivo
    ``env.yaml``
    :type: dict
    :returns: Campos incorrectamente configurados
    :rtype: list
    """
    wrong_configs = dict()
    error_configs, empty_configs = list(), list()
    minimal_fields = {"URL", "INDEX", "L1", "L2", "API", "DEBUG", "SECRET_KEY"}
    default_env = set_minimal_env()
    default_fields = default_env.keys()
    for field in default_fields:
        # Field is not in minimal env vars
        if field not in env_configs.keys():
            error_configs.append(field)
            # Secret Key must be setting
            if field == "SECRET_KEY":
                env_configs[field] = secrets.token_urlsafe(50)
            # Minimal fields must be setting. Using defaults
            elif field in minimal_fields:
                env_configs[field] = default_env[field]
            else:
                # For optional fields set at least empty
                env_configs[field] = ""
        # Field is empty
        elif env_configs[field] == "" or env_configs[field] == {}:
            empty_configs.append(field)
    wrong_configs = {"warn": empty_configs, "error": error_configs}
    return env_configs, wrong_configs
