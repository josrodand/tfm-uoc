import os
from dotenv import load_dotenv
import pickle
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores import FAISS
import faiss

from langchain_community.docstore.in_memory import InMemoryDocstore
from openai import RateLimitError
import time

from src.rag_app.setup.params import (
    EMBEDDING_MODEL, 
    FAISS_PERSIST_PATH, 
    BM25_PERSIST_PATH, 
    CHUNK_PROCESSING_SIZE, 
    SLEEP_TIME
)


class VectorStoreBuilder:
    
    def __init__(self, text_splits):

        self.text_splits = text_splits
        self.embeddings = self.get_embeddings()


    def get_embeddings(self, embedding_model = EMBEDDING_MODEL):

        load_dotenv()
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # Ajusta según la versión de tu Azure OpenAI
        embeddings = AzureOpenAIEmbeddings(
            model=embedding_model,
            azure_endpoint=api_base,
            api_key=api_key,
            openai_api_version=api_version
        )

        return embeddings



    def build_faiss_vector_store(
            self, 
            persist_path = FAISS_PERSIST_PATH, 
            chunk_processing_size=CHUNK_PROCESSING_SIZE, 
            sleep_time = SLEEP_TIME
        ):

        # Configuración
        documents = self.text_splits  # Tu lista de Document()s
        ids = [str(i + 1) for i in list(range(len(self.text_splits)))]       # Lista de IDs correspondientes

        # Inicializar FAISS
        index = faiss.IndexFlatL2(len(self.embeddings.embed_query("hello world")))
        print(f"🧠 FAISS index initialized with {len(self.embeddings.embed_query('hello world'))} dimensions.")
        vector_store = FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore= InMemoryDocstore(),
            index_to_docstore_id={}
        )

        # Procesamiento por lotes
        print(f"🧠 Processing {len(documents)} documents in chunks of {chunk_processing_size}...")
        total = len(documents)
        for i in range(0, total, chunk_processing_size):
            doc_chunk = documents[i:i + chunk_processing_size]
            id_chunk = ids[i:i + chunk_processing_size]

            success = False
            while not success:
                try:
                    vector_store.add_documents(documents=doc_chunk, ids=id_chunk)
                    print(f"✅ Chunk {i}–{i+len(doc_chunk)-1} added.")
                    success = True
                except RateLimitError:
                    print(f"⚠️ Rate limit alert. Waiting {sleep_time} s...")
                    time.sleep(sleep_time)
                except Exception as e:
                    print(f"❌ Unexpected Error in chunk {i}–{i+len(doc_chunk)-1}: {e}")
                    success = True  # Evita bucle infinito por errores irreparables

        print("🎉 All documents processed")

        vector_store.save_local(persist_path)
        print(f"✅ FAISS index saved to {persist_path}")


    def build_bm25_index(self, persist_path = BM25_PERSIST_PATH):
        
        print("🧠 Building BM25 index...")
        with open(persist_path, "wb") as f:
            pickle.dump(self.text_splits, f)

        print(f"✅ BM25 index saved to {persist_path}")