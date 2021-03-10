.. _instalation:

Instalación de Esquite
**********************

Instalación manual
==================

0. Instalar y ejecutar ``elasticsearch``

.. attention::

    El *framework* requiere de una instancia de ``elasticsearch`` previamente
    instalada. Para completar este requerimiento puedes consultar la `página
    oficial de Elasticsearch
    <https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html>`_

.. tip::

    El asistente de configuración :func:`wizard` configurará un índice de
    Elasticsearch con el archivo de configuración por defecto
    :ref:`index-config-file`. Puedes modificarlo a tu gusto siguiendo la
    `documentación de elasticsearch
    <https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-create-index.html#indices-create-api-request-body>`_.


1. Clona el repositorio::

    $ git clone https://github.com/ElotlMX/esquite

2. Crea un entorno virtual de ``python``::

    $ virtualenv env -p /usr/bin/python3

3. Activar el entorno::

    $ source env/bin/activate

4. Instalar las dependencias::

    (env)$ pip install -r requeriments.txt

5. Iniciar el asistente de instalación e ingresar los datos requeridos. Ver :func:`wizard` ::

    (env)$ python wizard.py

.. hint::

    El asistente :func:`wizard` creara un :ref:`config-file` llamado
    ``env.yaml`` donde se definen configuraciones de :ref:`colors`,
    :ref:`keyboard`, :ref:`contact`,
    entre otras.

    Este archivo debe estar en la raíz del proyecto.

6. Aplicar migraciones de ``django``::

    (env)$ python manage.py migrate

7. Correr ``django`` en segundo plano::

    (env)$ python manage.py runserver 0.0.0.0:8000 &

Imagen de Docker
================

Instalación de docker
---------------------

Si no tienes ``docker`` instalado puedes ejecutar los siguientes comandos para
instalarlo::

    curl -sSL https://get.docker.com | sh
    sudo service docker start
    pip3 install docker-compose

.. note::

    Elasticsearch necesita la siguiente configuración en producción: El valor de ``vm.max_map_count`` debe ser ``262144``. Para esto existen dos opciones:

    a. Cambio temporal::

        sysctl -w vm.max_map_count=262144

    b. Cambio permanente modificando ``/etc/sysctl.conf``::

        vm.max_map_count=262144

Iniciando el contenedor
-----------------------

1. Clona e ingresa al repositorio::

    git clone https://github.com/ElotlMX/Esquite-docker.git
    cd Esquite-docker

2.a Usando archivo de inicialización ``esquite-docker.sh``::

    sudo ./esquite-docker.sh start

2.b Usando `docker-compose` directamente::

    sudo docker-compose up -d

Navegando en la interfaz web
----------------------------

Ingresa a http://localhost. El password default para el administrador del corpus (``http://localhost/corpus-admin/``) es **elotl**.

.. hint::

    Puedes cambiar el password por defecto cambiandop la variable `CFG_CORPUS_ADMIN_PASS=elotl` en el archivo `docker-compose.yml`.

.. note::

    `sudo` es necesario ya que por default `Docker` necesita permisos de `root` para
    crear nuevos container. Sin embargo esto se puede cambiar si se le asigna a un
    usuario específico permisos para ejecturar `Docker`.

Opciones
--------

Al ejecutar ``esquite-docker.sh`` aparecen las opciones disponibles::

    ##############################################
     Esquite Docker script   - Comunidad ElotlMX
    ----------------------------------------------
     Github: https:///github.com/elotlmx
     Web   : Elotl.mx
    ##############################################


    [EN ] ERROR: Unknown Option: Syntax:    ./esquite-docker (start|stop|restart|destroy|info|update|recreate)
    [ES ] ERROR: Opción no valida. Sintaxis:    ./esquite-docker (iniciar|detener|reiniciar|destruir|info|actualizar|recrear)
    [NAH] TLATLACOLLI: Opción no valida. Sintaxis:    ./esquite-docker (pehualtia|cahua|re-pehualtia|tlapoloa|tlanonotzaliztli|yancuic|tlaana)

Opciones de Docker compose
^^^^^^^^^^^^^^^^^^^^^^^^^^

Opciones generales
""""""""""""""""""

El archivo de configuración de ``docker-compose.yml`` se puede personalizar para
las opciones generales de Esquite.

Índice externo de Elasticsearch
"""""""""""""""""""""""""""""""

Si se desea usar un indice externo de Elasticseach, solo se deben cambiar las
variables ``CFG_URL`` y ``CFG_INDEX``. Si estas opciones no se modifican, se creará
un índice automáticamente en un container generado por el script de
inicialización

Actualización de versión de Esquite
"""""""""""""""""""""""""""""""""""

Se puede habilitar la actualización de Esquite cada vez que se reinicie el
container activando la opción ``CFG_UPDATE_ON_BOOT`` o manualmente por medio de
las opciones ``update`` o ``actualizar`` o ``tlanonotzaliztli`` con el script
``./esquite-docker.sh``

