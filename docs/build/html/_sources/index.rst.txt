.. Corpus Paralelo Backend documentation master file, created by
   sphinx-quickstart on Fri Apr 10 18:41:31 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentación del Backend de Corpus Paralelo
=============================================

Se rescatan ciertas consideraciones importantes

* **Vistas**: Estas funciones se encargan de procesar los datos que otorgan
  las usuarias para ser procesados y posteriorimente *renderean* los archivos
  ``html`` con la información solicitada. Ej: Una consulta al índice de
  Elasticsearch, las personas involucradas en el proyecto, etc.
* **Rutas**: En esta sección se configuran el nombre de las rutas del proyecto.
  Las rutas son el texto que aparece en la parte superior del navegador.
  Por ejemplo las que se muestran a continuación:

  * ``https://tsunkua.elot.mx/about/``
  * ``https://tsunkua.elotl.mx/media/visiondelosvencidoshnahnu.pdf/``

* **Formularios**: Los formularios mostrados en las vistas son generados por
  medio de las clases de ``django`` ya que brindan ventajas conrespecto a
  validaciones, paso de datos de las vistas a los controladores, etc.
* **Funciones auxiliares**: Funciones que son útiles en diversos escenarios.
  Sobre todo es un archivo para organizar funciones con diversos propositos.

.. toctree::
   :maxdepth: 2
   :caption: Aplicaciones:

   install
   tutorials
   elotl
   searcher
   corpus_admin
   wizard

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
