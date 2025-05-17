from src.rag_app.setup.load import RAGLoader
from src.rag_app.setup.processing import RAGProcessing
from rag_app.setup.vector_store_builder import VectorStoreBuilder


class RAGSetup:
    """
    A class to set up and run the RAG (Retrieval-Augmented Generation) pipeline.
    Methods
    -------
    __init__():
        Initializes the RAGSetup instance.
    run():
        Executes the RAG pipeline, which includes:
        - Loading documents using RAGLoader.
        - Processing documents into text splits using RAGProcessing.
        - Building a FAISS vector store and a BM25 index using VectorStoreBuilder.
    """

    def __init__(self):
        pass


    def run(self):
        """
        Executes the RAG (Retrieval-Augmented Generation) setup process.
        This method performs the following steps:
        1. Loads documents using the RAGLoader.
        2. Processes the loaded documents using RAGProcessing to generate text splits.
        3. Builds a FAISS vector store and a BM25 index using the processed text splits.
        Steps:
        - Initializes a RAGLoader instance to load documents.
        - Processes the documents using standard processing to split text into smaller chunks.
        - Initializes a VectorStoreBuilder with the processed text splits.
        - Builds a FAISS vector store for efficient similarity search.
        - Builds a BM25 index for traditional keyword-based search.
        Prints progress and status updates during the execution.
        Raises:
            Any exceptions raised during document loading, processing, or index building.
        """

        rag_loader = RAGLoader()

        print("Loading documents...")
        documents = rag_loader.load_documents()
        print(f"Loaded {len(documents)} documents.")

        print("Processing documents...")
        rag_processing = RAGProcessing(documents)
        text_splitts = rag_processing.standard_processing()
        print(f"Processed {len(text_splitts)} text splits.")

        vector_sotre_builder = VectorStoreBuilder(text_splitts)
        vector_sotre_builder.build_faiss_vector_store()
        vector_sotre_builder.build_bm25_index()