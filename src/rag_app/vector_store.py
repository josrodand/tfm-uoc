import os
from dotenv import load_dotenv
import pickle
from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.retrievers import BM25Retriever, EnsembleRetriever
# import faiss

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import FlashrankRerank
from flashrank import Ranker

from src.rag_app.setup.params import (
    EMBEDDING_MODEL, 
    FAISS_PERSIST_PATH, 
    BM25_PERSIST_PATH
)


class VectorStore:
    """
    VectorStore is a utility class for managing and retrieving embeddings and documents using various retrieval methods.
    Attributes:
        k (int): The number of documents to retrieve. Defaults to 3.
        embeddings (AzureOpenAIEmbeddings): The embeddings model used for vector-based retrieval.
    Methods:
        get_embeddings(embedding_model=EMBEDDING_MODEL):
            Initializes and returns an AzureOpenAIEmbeddings instance using environment variables for configuration.
        faiss_retriever():
            Loads a FAISS vector store from a local path and returns a retriever configured to retrieve `k` documents.
        bm25_retriever():
            Loads BM25 data from a local pickle file and returns a BM25Retriever configured to retrieve `k` documents.
        ensemble_retriever():
            Combines the FAISS and BM25 retrievers into an EnsembleRetriever with equal weights and returns it.
        rerank_retriever():
            Creates a reranking retriever by combining the ensemble retriever with a contextual compression retriever.
            Returns the compression-based reranking retriever.
    """

    def __init__(self, k_documents = 3):

        self.embeddings = self.get_embeddings()
        self.k = k_documents


    def get_embeddings(self, embedding_model = EMBEDDING_MODEL):
        """
        Retrieves embeddings using the specified embedding model and Azure OpenAI service.
        This method loads environment variables to configure the Azure OpenAI API, 
        including the API key, endpoint, and version. It then initializes and returns 
        an AzureOpenAIEmbeddings object with the specified embedding model.
        Args:
            embedding_model (str): The name of the embedding model to use. Defaults to EMBEDDING_MODEL.
        Returns:
            AzureOpenAIEmbeddings: An instance of the AzureOpenAIEmbeddings class configured 
            with the specified model and Azure OpenAI API settings.
        Environment Variables:
            AZURE_OPENAI_API_KEY (str): The API key for accessing Azure OpenAI.
            AZURE_OPENAI_ENDPOINT (str): The endpoint URL for the Azure OpenAI service.
            AZURE_OPENAI_API_VERSION (str): The API version to use with Azure OpenAI.
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


    def faiss_retriever(self):
        """
        Creates and returns a FAISS retriever instance.
        This method loads a FAISS vector store from a local path, using the specified
        embeddings and allowing potentially unsafe deserialization. It then converts
        the vector store into a retriever with the specified search parameters.
        Returns:
            retriever: A retriever instance configured to perform similarity search
                    with the specified number of nearest neighbors (`k`).
        """

        vector_store = FAISS.load_local(
            FAISS_PERSIST_PATH, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": self.k})

        return retriever
    
    def bm25_retriever(self):
        """
        Creates and returns a BM25Retriever instance using preloaded BM25 data.
        This method loads BM25 data from a persistent storage file, initializes
        a BM25Retriever object with the loaded data, and sets the number of 
        top documents to retrieve (`k`) based on the instance attribute.
        Returns:
            BM25Retriever: An instance of BM25Retriever initialized with the 
            preloaded BM25 data and configured with the specified number of 
            top documents to retrieve.
        Raises:
            FileNotFoundError: If the BM25 persistence file is not found.
            pickle.UnpicklingError: If there is an error unpickling the BM25 data.
        """

        with open(BM25_PERSIST_PATH, "rb") as f:
            bm25_data = pickle.load(f)
        keyword_retriever = BM25Retriever.from_documents(bm25_data)
        keyword_retriever.k =  self.k

        return keyword_retriever
    

    def ensemble_retriever(self):
        """
        Creates and returns an ensemble retriever that combines multiple retrieval methods.
        This method initializes two retrievers: a FAISS-based retriever and a BM25-based retriever.
        It then combines them into an ensemble retriever using specified weights for each retriever.
        Returns:
            EnsembleRetriever: An ensemble retriever that combines FAISS and BM25 retrievers
            with equal weighting.
        """
        faiss_retriever = self.faiss_retriever()
        bm25_retriever = self.bm25_retriever()

        ensemble_retriever = EnsembleRetriever(
            retrievers=[faiss_retriever, bm25_retriever],
            weights=[0.5, 0.5]
        )

        return ensemble_retriever


    def rerank_retriever(self):
        """
        Creates and returns a ContextualCompressionRetriever instance that combines 
        an ensemble retriever, a ranker, and a compressor for reranking retrieved results.
        The method initializes an ensemble retriever, a ranker, and a FlashrankRerank 
        compressor. It then uses these components to create a ContextualCompressionRetriever, 
        which applies contextual compression to the retrieval process.
        Returns:
            ContextualCompressionRetriever: A retriever that performs reranking and 
            contextual compression on retrieved results.
        """

        ensemble_retriever = self.ensemble_retriever()
        ranker = Ranker()
        compressor = FlashrankRerank()
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, 
            base_retriever=ensemble_retriever
        )

        return compression_retriever