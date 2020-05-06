Programa de intalación wizard.py
================================

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

    ALT_TEXT: '#ffffff'
    COLABS:
    - Hari Seldon
    - Salvon Hardin
    - Hober Mallow
    - Bayta Darrell
    - Arkady Darrell
    DEBUG: 'False'
    KEYBOARD:
    GOOGLE_ANALYTICS: 'UA-XXXXXXXXX-X'
    INDEX: index-name
    LANG_1: "Español"
    LANG_2: "Galactico"
    NAME: ENCICLOPEDIA GALACTICA
    ORG_NAME: FUNDACION
    PRIMARY_COLOR: '#ffffff'
    SECONDARY_COLOR: '#000000'
    SECRET_KEY: '"<llave-secreta-autogenerada>"'
    SOCIAL:
      site: https://example.com/
      blog: https://example.com/blog/
      email: mail@example.com
      facebook: https://www.facebook.com/fundacion/
      twitter: https://twitter.com/fundacion/
      github: https://github.com/fundacion/
    TEXT_COLOR: '#000000'
    URL: http://elasticsearch-ip:9600/

.. warning::

    La variable llamada ``DEBUG`` está establecida por defecto en ``FALSE``
    siguiendo las recomendaciones de seguridad de ``django`` para un entorno
    de **producción**.

    En este estado el servidor web de ``django`` no está habilitado, por
    lo que, los archivos estáticos (``js``, ``css``, imagenes, entre otros)
    no se cargarán. Para ello se deberá configurar un servidor web externo
    como `nginx <https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/>`_
    , `apache <https://httpd.apache.org/download.cgi>`_ u otro.

    Si se está en un entorno de **desarrollo** se puede cambiar el valor
    de la variable a ``TRUE`` con lo que se habilitará el servidor web de
    ``django``. Además, si existen excepciones se mostrará un detallado
    *traceback*, que incluye muchos metadatos del entorno, en el navegador web.

    Recomendamos ampliamente leer la
    `documentación sobre esta variable <https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-DEBUG>`_



Funciones del script
--------------------

.. automodule:: wizard
   :members:
   :undoc-members:
   :show-inheritance:
