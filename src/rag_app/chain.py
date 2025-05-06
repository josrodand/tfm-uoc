
import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.rag_app.vector_store import VectorStore
from src.rag_app.prompts import RAG_PROMPT


class RAGChain:
    
    def __init__(self, retriever_mode = "rerank"):

        self.rag_prompt = RAG_PROMPT
        self.retriever = self.get_retriever(retriever_mode=retriever_mode)
        self.llm = self.get_llm()
        self.chain = self.get_chain()

    #llm
    def get_llm(self):

        load_dotenv()
        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("03_MINI_DEPLOYMENT")  # nombre del *deployment*, NO del modelo
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # Ajusta según la versión de tu Azure OpenAI

        llm = AzureChatOpenAI(
            openai_api_key=api_key,
            azure_endpoint=api_base,
            deployment_name=deployment,
            api_version=api_version,
            # temperature=0
        )

        return llm


    # retriever
    def get_retriever(self, retriever_mode = "rerank"):

        vector_store = VectorStore()

        if retriever_mode == "faiss":
            retriever = vector_store.faiss_retriever()

        elif retriever_mode == "ensemble":
            retriever = vector_store.ensemble_retriever()

        elif retriever_mode == "rerank":
            retriever = vector_store.rerank_retriever()

        else:
            raise ValueError("Invalid retriever mode. Choose 'faiss', 'ensemble', or 'rerank'.")
        
        return retriever
    
    # chain
    def get_chain(self):
        
        prompt = ChatPromptTemplate.from_template(RAG_PROMPT)
        output_parser = StrOutputParser()

        chain = (
            {"context": self.retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | output_parser
        )

        return chain


    # source extraction
    def get_retrieved_docs(self, query):
    # return vector_store.similarity_search(query, k=5)
        return self.retriever.invoke(query)


    def serialize_docs(self, retrieved_docs):
        sources = "Fuentes:\n"
        for doc in retrieved_docs:
            source = doc.metadata['source']
            try:
                page = doc.metadata['page']
            except KeyError:
                page = None
            new_source = f"* {source}, Página: {page}\n" if page else f"* {source}\n"
            sources += new_source

        return sources


    def get_sources(self, query):

        retrieved_docs = self.get_retrieved_docs(query)
        sources = self.serialize_docs(retrieved_docs)
        return sources
    

    def invoke(self, query):

        response = self.chain.invoke(query)
        sources = self.get_sources(query)
        response_sources = response + "\n\n" + sources

        return response_sources