# repo schema


# extractor
Modulo principal del extractor

* core
    * base_extractor
* params
    * extraction_params
* cdti
    * cdti_matrix_extractor
    * cdti_aid_extractor
    * cdti_pipeline
* generic_aid
    * generic_aid_mainpage_extraction
        * algo similar a la matriz del cdti
    * generic_aid_extractor
    * generic_aid_pipeline
* pipeline
    * extraction_pipeline

# data
Almacenamiento en local de la base de conocimiento

* cdti
    * cdti_matrix.json
    * aid_1
        * aid_ficha(.json): ficha de la ayuda
        * aid_doc.pdf: pdf de la ayuda
    * ...


# data_processing
Modulo de procesado de las fuentes de datos
* extraccion de entidades
* preprocesamiento para rag
    * pdf to markdown
    * chunks
    * contextual rag preproccessing
    * ...

# contextual_rag_agent
RAG empleando técnicas:
* agente hibrido de consulta a RAG o SQL
* RAG contextual
* Busqueda hibrida: vectorial + BM25