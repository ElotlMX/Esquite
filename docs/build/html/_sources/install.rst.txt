Instalación
===========

1. Clona el repositorio::
        
    $ git clone esquite

2. Crea un entorno virtual de ``python``::

    $ virtualenv env -p /usr/bin/python3

3. Activar el entorno::

    $ source env/bin/activate

4. Instalar las dependencias::

    (env)$ pip install -r requeriments.txt

5. Iniciar el asistente de instalación e ingresar los datos requeridos. Ver
   :func:`wizard` ::

    (env)$ python wizard.py

6. Correr ``django`` en segundo plano::

    (env)$ python manage.py runserver 0.0.0.0:3000 &

.. note::

  Se requiere un índice de Elasticsearch previamente configurado como se ve en
  la :ref:`elastic-configuration` para ser indicado en la configuración de
  :func:`wizard`

  El :ref:`config-file` es creado automáticamente por el asistente de
  instalación :func:`wizard`. Este archivo debe estar en la raíz del
  proyecto.
