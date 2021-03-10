Asistente de instalación ``wizard.py``
======================================

Este programa se encarga de asistir a la usuaria a generar el archivo
``env.yaml`` que contiene las configuraciones generales del proyecto.
El archivo mencionado es **necesario** para que el proyecto funcione
correctamente.

Configuraciones
---------------

Un archivo ``env.yaml`` típico para el proyecto y generado por el asistente
de configuración se verá de la siguiente manera:


.. _config-file:

Archivo de configuración
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: yaml

    API:
      limit_results:
        anon: 10
        user: 100
      num_proxies: 0
      throttles:
        burst_anon: 20/hour
        burst_user: 50/hour
        sustain_anon: 50/day
        sustain_user: 200/day
    COLABS:
      - Hari Seldon
      - Salvon Hardin
      - Hober Mallow
      - Bayta Darrell
      - Arkady Darrell
    DEBUG: 'True'
    KEYBOARD:
      - a
      - b
      - c
      - d
    GOOGLE_ANALYTICS: 'UA-XXXXXXXXX-X'
    INDEX: index-name
    L1: "Español"
    L2: "Galactico"
    NAME: ENCICLOPEDIA GALACTICA
    ORG_NAME: FUNDACION
    COLORS:
      background:
        btnhover: '#69c9be'
        button: '#06a594'
        footer: '#ffffff'
        form: '#fdecb2'
        highlight: '#fdecb2'
        nav: '#fbda65'
      border:
        button: '#06a594'
        input: '#06a594'
      text:
        bold: '#06a594'
        btnhover: '#fbda65'
        button: '#ffffff'
        footer: '#000000'
        form: '#000000'
        highlight: '#048476'
        hoverlinks: '#69c9be'
        links: '#06a594'
        nav: '#06a594'
        navactive: '#048476'
        navhover: '#69c9be'
        result: '#000000'
    SECRET_KEY: '"<llave-secreta-autogenerada>"'
    LINKS:
        social:
          site: https://example.com/
          blog: https://example.com/blog/
          email: mail@example.com
          facebook: https://www.facebook.com/fundacion/
          twitter: https://twitter.com/fundacion/
          github: https://github.com/fundacion/
        corpora:
            axolotl: "https://www.axolotl-corpus.mx/search"
            kolo: "https://kolo.elotl.mx/"
            job: "https://job.elotl.mx/"
    URL: http://elasticsearch-ip:9600/
    META_DESC: Corpus paralelo del Español al Galactico.

.. warning::

    La variable llamada ``DEBUG`` está establecida por defecto en ``True``
    dado que es mas conveniente. Pero, las recomendaciones de seguridad
    de ``django`` sugieren el modo ``DEBUG`` en ``False`` para un entorno de
    **producción**.

    Sin embargo, con el modo ``DEBUG`` en ``False`` el servidor web de
    ``django`` no está habilitado, por lo que, los archivos estáticos (``js``,
    ``css``, imagenes, entre otros) no se cargarán. Para ello se deberá
    configurar un servidor web externo como `nginx
    <https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/>`_
    , `apache <https://httpd.apache.org/download.cgi>`_ u otro.

    El valor de la variable ``DEBUG`` en ``True`` es para un entorno de
    **desarrollo**. En este entorno se habilitará el servidor web de
    ``django``. Además, si hubiese un error se mostraran, en el navegador, un
    detallado *traceback* que incluye muchos metadatos del entorno.

    Recomendamos ampliamente leer la
    `documentación sobre esta variable <https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-DEBUG>`_



Funciones del script
--------------------

.. automodule:: wizard
   :members:
   :undoc-members:
   :show-inheritance:
