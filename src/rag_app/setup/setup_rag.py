from src.rag_app.setup.load import RAGLoader
from src.rag_app.setup.processing import RAGProcessing
from rag_app.setup.vector_store_builder import VectorStoreBuilder


class RAGSetup:

    def __init__(self):
        pass


    def run(self):

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