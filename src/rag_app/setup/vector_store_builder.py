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
    """
    A class to build and manage vector stores and BM25 indices for document embeddings.
    Attributes:
        text_splits (list): A list of text documents to be processed.
        embeddings (AzureOpenAIEmbeddings): An instance of AzureOpenAIEmbeddings for generating embeddings.
    Methods:
        __init__(text_splits):
            Initializes the VectorStoreBuilder with a list of text documents and sets up embeddings.
        get_embeddings(embedding_model=EMBEDDING_MODEL):
            Retrieves the embedding model using Azure OpenAI configurations.
        build_faiss_vector_store(persist_path=FAISS_PERSIST_PATH, chunk_processing_size=CHUNK_PROCESSING_SIZE, sleep_time=SLEEP_TIME):
            Builds a FAISS vector store from the provided text documents, processes them in chunks, and saves the index locally.
        build_bm25_index(persist_path=BM25_PERSIST_PATH):
            Builds a BM25 index from the provided text documents and saves it locally.
    """
    
    def __init__(self, text_splits):

        self.text_splits = text_splits
        self.embeddings = self.get_embeddings()


    def get_embeddings(self, embedding_model = EMBEDDING_MODEL):
        """
        Retrieves embeddings using the Azure OpenAI service.
        This method initializes and returns an instance of `AzureOpenAIEmbeddings` 
        configured with the specified embedding model and Azure OpenAI API credentials.
        Args:
            embedding_model (str, optional): The name of the embedding model to use. 
                Defaults to the value of the `EMBEDDING_MODEL` constant.
        Returns:
            AzureOpenAIEmbeddings: An instance of the Azure OpenAI embeddings class 
            configured with the provided or default model and API credentials.
        Environment Variables:
            AZURE_OPENAI_API_KEY: The API key for authenticating with Azure OpenAI.
            AZURE_OPENAI_ENDPOINT: The base endpoint URL for the Azure OpenAI service.
            AZURE_OPENAI_API_VERSION: The version of the Azure OpenAI API to use.
        """

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
        """
        Builds and saves a FAISS vector store from the provided text splits.
        This method processes the documents in chunks, embeds them using the 
        provided embedding function, and adds them to a FAISS index. The index 
        is then saved locally to the specified path.
        Args:
            persist_path (str): The file path where the FAISS index will be saved. 
                Defaults to FAISS_PERSIST_PATH.
            chunk_processing_size (int): The number of documents to process in 
                each batch. Defaults to CHUNK_PROCESSING_SIZE.
            sleep_time (int): The time in seconds to wait before retrying in case 
                of a rate limit error. Defaults to SLEEP_TIME.
        Raises:
            RateLimitError: If the embedding function exceeds its rate limit. 
                The method will retry after waiting for `sleep_time` seconds.
            Exception: For any other unexpected errors during document processing.
        Notes:
            - The method assumes `self.text_splits` contains the list of documents 
            to be processed.
            - Each document is assigned a unique ID based on its position in the 
            list.
            - The FAISS index is initialized with the dimensionality of the 
            embedding function's output.
            - The method handles rate limit errors by retrying after a delay, and 
            logs any unexpected errors without halting the process.
        """
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
        """
        Builds and saves a BM25 index using the text splits stored in the instance.
        Args:
            persist_path (str): The file path where the BM25 index will be saved. 
                                Defaults to the value of BM25_PERSIST_PATH.
        Side Effects:
            - Serializes the text splits into a file at the specified path using pickle.
        Prints:
            - A message indicating the start of the BM25 index building process.
            - A confirmation message with the path where the BM25 index is saved.
        """
        
        print("🧠 Building BM25 index...")
        with open(persist_path, "wb") as f:
            pickle.dump(self.text_splits, f)

        print(f"✅ BM25 index saved to {persist_path}")