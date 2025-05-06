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

    def __init__(self, k_documents = 3):

        self.embeddings = self.get_embeddings()
        self.k = k_documents


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


    def faiss_retriever(self):

        vector_store = FAISS.load_local(
            FAISS_PERSIST_PATH, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )

        retriever = vector_store.as_retriever(search_kwargs={"k": self.k})

        return retriever
    
    def bm25_retriever(self):

        with open(BM25_PERSIST_PATH, "rb") as f:
            bm25_data = pickle.load(f)
        keyword_retriever = BM25Retriever.from_documents(bm25_data)
        keyword_retriever.k =  self.k

        return keyword_retriever
    

    def ensemble_retriever(self):
        faiss_retriever = self.faiss_retriever()
        bm25_retriever = self.bm25_retriever()

        ensemble_retriever = EnsembleRetriever(
            retrievers=[faiss_retriever, bm25_retriever],
            weights=[0.5, 0.5]
        )

        return ensemble_retriever


    def rerank_retriever(self):

        ensemble_retriever = self.ensemble_retriever()
        ranker = Ranker()
        compressor = FlashrankRerank()
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor, 
            base_retriever=ensemble_retriever
        )

        return compression_retriever