.. _instalation:

Instalación
===========

0. Instalar y ejecutar ``elasticsearch``

.. note::

    El *framework* requiere de una instancia de ``elasticsearch`` previamente
    instalada. Para completar este requerimiento puedes consultar la `página
    oficial de Elasticsearch
    <https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html>`_

    Además, es necesario configurar un índice de Elasticsearch
    con la información que se ve en la :ref:`elastic-configuration`.

    El :ref:`config-file` del proyecto es creado automáticamente por el
    asistente de instalación :func:`wizard`. Este archivo debe estar en la raíz
    del proyecto.  El nombre del índice debe ser indicado cuando se corre el
    asistente de configuración :func:`wizard`.

1. Clona el repositorio::

    $ git clone https://github.com/ElotlMX/esquite

2. Crea un entorno virtual de ``python``::

    $ virtualenv env -p /usr/bin/python3

3. Activar el entorno::

    $ source env/bin/activate

4. Instalar las dependencias::

    (env)$ pip install -r requeriments.txt

5. Iniciar el asistente de instalación e ingresar los datos requeridos. Ver
   :func:`wizard` ::

    (env)$ python wizard.py

6. Aplicar migraciones de ``django``::

    (env)$ python manage.py migrate

7. Correr ``django`` en segundo plano::

    (env)$ python manage.py runserver 0.0.0.0:8000 &


