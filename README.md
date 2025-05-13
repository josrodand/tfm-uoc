# tfm-uoc
Repositorio del TFM del Máster Universitario en Ciencia de Datos


# Descripción del contenido

Modulos:
* **extraction**: Modulo de scraping.
* **processing**: Módulo de procesado para la construcción de la tabla de datos estructurados.
* **rag_app**: Módulo de aplicación de RAG multiagente.


# Puesta en funcionamiento

* **run_extraction.py**: Ejecuta el scraping y vuelca los documentos en el directorio data.
    * nota: Es necesario descargar el chromedriver y añadir en el codigo el directorio donde se encuentre.
* **run_processing.py**: Ejecuta el procesado de datos y genera un fichero csv con la tabla de ayudas.
    * La ayuda "invierte" da error al estar vacía. De momento hay que borrar la carpeta de la ayuda a mano.  
* **run_rag_setup.py**: Levanta en local las fuentes de datos a partir del directorio data: Base de datos SQLite y vectorstore con FAISS.
* **streamlit_app.py**: App en streamlit de asistente conversacional multiagente.