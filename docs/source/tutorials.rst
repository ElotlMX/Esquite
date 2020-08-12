.. _tutorials:

Tutoriales
==========

Personalización
---------------

Colores
```````

La personalización de colores está limitada a los fondos, texto y bordes de
botones. Modificando la variable ``COLORS`` que tiene formato de diccionario se
pueden alterar los colores de las vistas por elemento ``HTML``. La variable
tiene el siguiente formato:

.. code-block:: yaml

  COLORS:
    background:
      button: '#aa4678'
      form: '#e3cee3'
      hover: '#bf6492'
      nav: '#e3cee3'
    border:
      button: '#aa4678'
    text:
      button: 'white'
      form: 'black'
      highlight: '#aa4678'
      hover: 'white'
      nav: 'black'
      result: '#aa4678'

Se puede utilizar formato hexadecimal (``#fffffff``) o el nombre en inglés del
color si es un `color soportado <https://www.w3schools.com/cssref/css_colors.asp>`_
por ``css``. 


Teclado
```````

El corpus permite agregar teclas personalizadas para la lengua *l2* con 
caracteres que no estén en el teclado físico o que sean difíciles de obtener.
Para agregar teclas personalizadas se debe modificar la variable ``KEYBOARD``
del archivo ``env.yaml`` agregando cada tecla en un renglón. A continuación se
muestra un ejemplo

.. code-block:: yaml

        KEYBOARD:
        - u̱
        - e̱
        - a̱
        - i̱
        - o̱
        - ŭ
        - ä
        - "'"

.. image:: ../img/keyboard.png

.. note::

  Se debe agregar el guión antes de cada letra para que se pueda interpretar
  como una lista de caractéres. Tambien se puede usar una sintaxis de lista
  tipo python como ``KEYBOARD: [u̱, e̱, a̱, i̱, o̱, ŭ, ä, "'"]``.

Datos de contacto
`````````````````

Se pueden agregar las redes sociales y datos de contacto de la organización.
Dicho datos aparecen en la vista de ``participantes``. Para agregar estos datos
se debe modificar la variable ``SOCIAL``. Esta variable tiene un formato de 
diccionario.

.. code-block:: yaml


        SOCIAL:
          site: 'https://mi_sitio.mx/'
          blog: 'https://mi_sitio.mx/blog/'
          email: 'contacto@mi_sitio.mx'
          facebook: 'https://facebook.com/mi_sitio'
          github: 'https://github.com/mi_sitio'
          twitter: 'https://twitter.com/mi_sitio'

Colaboradorxs
`````````````

Si el desarrollo del proyecto que estas elaborando tiene más personas
involucradas es posible modificar la variable ``COLABS`` para agregar los
nombres de estas personas. Dichos nombres se desplegaran en la vista de
``participantes``.

.. code-block:: yaml

  COLABS:
    - Hari Seldon
    - Salvon Hardin
    - Hober Mallow
    - Bayta Darrell
    - Arkady Darrell

Modificación del banner
```````````````````````

El banner por defecto puede ser remplazado modificando el archivo
que se encuentra en la ruta ``static/img/banner.png``. El archivo **debe**
llamarse ``banner.png``. Se recomienda utilizar una imagen de ``1260 x 270
pixeles``. 

Vistas
``````

Es posible extender las vistas de ``Ayuda``, ``Ligas de
interés``, ``Acerca del Corpus`` y ``Participantes`` con
información específica del proyecto.

Para agregar información a las vistas se deben modificar los archivos que se
encuentran en la ruta ``tamplates/user/``. Cada archivo hace referencia a la
vista que se modificará. El formato de los archivos es ``html``.

Por ejemplo, si deseas extender la sección de ayuda puedes modificar el
archivo ``templates/user/help-user.html``. Si agregas el siguiente código
``html`` se obtiene el resultado de la imagen.

.. code-block:: html

  <h4>Consideraciones para el galáctico</h4>
  La escritura del galáctico es ampliamente reconocida por todos los sistemas pertenecientes al Imperio. Se deben tomar las siguientes consideraciones:

  <ul>
    <li>Utilizar las grafía estandar en las búsquedas que son dadas en el teclado</li>
    <li>Si no encuentras la gráfia necesarias en el teclado puedes buscarla en la Enciclopedia galáctica.</li>
    <li>Si necesitas algun recurso como un libro-película contactano en <a href="http://www.imperio.com" target="_blank">esta dirección</a></li>
  </ul>


.. image:: ../img/help-user.png

Administración del corpus
-------------------------

Subida de documentos
````````````````````

La aplicación provee una interface interna de *administración del corpus* que
puede encontrarse en la url ``https://micorpus.com/corpus-admin/``.
Si se quiere subir material al corpus deberá ser en formato ``.csv``
(**separado por comas**).

Es **indispensable** que exista la cabecera ya que la primer línea
del archivo se **ignora** por defecto. Actualmente se tiene la siguiente
convención para la subida de nuevos documentos

.. image:: ../img/corpus_table.png

Primera columna la lengua l1 (en este ejemplo español), segunda columna la
lengua l2 (en este ejemplo otomí) y en la última columna la variante. Además,
cada documento deberá tener asociado un archivo ``.PDF`` con fines ilustrativos
para lxs usuarixs.

.. note::
  En caso de que la variante tenga ISO se requiere que venga entre
  paréntesis al final del nombre de la variante como se muestra en la tabla
  anterior.

  Si no existe variante para el documento dicha columna **deberá** existir pero
  estará vacía.


Configuración
-------------

.. _elastic-configuration:

Creación del índice de elasticsearch
````````````````````````````````````

El *framework* requiere de un índice de elasticsearch configurado. Para crear
el índice es necesario que una instancia de ``elasticsearch`` este instalada y
corriendo. Se puede utilizar el comando ``curl`` como se muestra a continuación:
  
.. code-block:: shell

  $ curl -X PUT -H "Content-Type: application/json" -d @elastic-config.json localhost:9200/<nombre-de-tu-indice>

La configuración utilizada se encuentra en el archivo ``elastic-config.json``
que está en el repositorio. Esta configuración esta optimizada para que a la
lengua *l1* se le aplique un preprocesamiento asumiendo que es el idioma español
para que las búsquedas tomen en cuenta las *stopwords*.

``elastic-config.json``
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: json

  {
    "settings": {
      "index": {
        "number_of_shards": 1,
        "analysis": {
          "filter": {
            "spanish_stop": {
                "type":       "stop",
                "stopwords":  "_none_"
              },
            "spanish_stemmer": {
              "type": "stemmer",
              "language": "light_spanish"
            }
          },
          "analyzer": {
            "rebuild_spanish": {
              "tokenizer":  "standard",
              "filter": [
                "lowercase",
                "spanish_stop",
                "spanish_stemmer"
              ]
            }
          }
        }
      }
    },
    "mappings": {
      "properties": {
        "pdf_file": {
          "type": "keyword"
        },
        "document_id": {
          "type": "keyword"
        },
        "document_name": {
          "type": "keyword"
        },
        "l1": {
          "type": "text",
          "analyzer":"rebuild_spanish"
        },
        "l2": {
          "type": "text"
        },
        "variant": {
          "type": "keyword"
        }
      }
    }
  }
