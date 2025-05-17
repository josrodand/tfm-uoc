
import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from src.rag_app.vector_store import VectorStore
from src.rag_app.prompts import RAG_PROMPT


class RAGChain:
    """
    RAGChain is a class designed to implement a Retrieval-Augmented Generation (RAG) pipeline. 
    It integrates a retriever, a language model (LLM), and a chain to process queries and generate responses.
    Attributes:
        rag_prompt (str): The prompt template used for the RAG pipeline.
        retriever (object): The retriever instance used to fetch relevant documents.
        llm (object): The language model instance used for generating responses.
        chain (object): The chain that combines the retriever, prompt, LLM, and output parser.
    Methods:
        __init__(retriever_mode="rerank"):
            Initializes the RAGChain instance with the specified retriever mode.
        get_llm():
            Configures and returns the AzureChatOpenAI language model instance.
        get_retriever(retriever_mode="rerank"):
            Configures and returns the retriever based on the specified mode.
            Modes available: "faiss", "ensemble", "rerank".
        get_chain():
            Constructs and returns the chain that processes queries using the retriever, prompt, LLM, and output parser.
        get_retrieved_docs(query):
            Retrieves documents relevant to the given query using the retriever.
        serialize_docs(retrieved_docs):
            Serializes the retrieved documents into a formatted string of sources.
        get_sources(query):
            Retrieves and serializes the sources for the given query.
        invoke(query):
            Processes the query through the chain, retrieves sources, and combines the response with the sources.
    """
    
    def __init__(self, retriever_mode = "rerank"):

        self.rag_prompt = RAG_PROMPT
        self.retriever = self.get_retriever(retriever_mode=retriever_mode)
        self.llm = self.get_llm()
        self.chain = self.get_chain()

    #llm
    def get_llm(self):
        """
        Initializes and returns an AzureChatOpenAI instance configured with environment variables.
        This method loads environment variables using `load_dotenv()` and retrieves the necessary
        configuration for connecting to an Azure OpenAI deployment. The configuration includes:
        - `AZURE_OPENAI_API_KEY`: The API key for authenticating with Azure OpenAI.
        - `AZURE_OPENAI_ENDPOINT`: The base URL for the Azure OpenAI endpoint.
        - `03_MINI_DEPLOYMENT`: The name of the deployment (not the model name).
        - `AZURE_OPENAI_API_VERSION`: The API version to use.
        Returns:
            AzureChatOpenAI: An instance of the AzureChatOpenAI class configured with the specified
            API key, endpoint, deployment name, and API version.
        """

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
        """
        Retrieves a retriever object based on the specified retriever mode.
        Args:
            retriever_mode (str): The mode of the retriever to use. Options are:
                - "faiss": Uses the FAISS-based retriever.
                - "ensemble": Uses the ensemble retriever.
                - "rerank": Uses the rerank retriever (default).
        Returns:
            object: The retriever object corresponding to the specified mode.
        Raises:
            ValueError: If an invalid retriever mode is provided.
        """

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
        """
        Constructs and returns a processing chain for handling input questions
        and retrieving context-based responses.
        The chain performs the following steps:
        1. Passes the input question through a retriever to obtain relevant context.
        2. Formats the context and question using a chat prompt template.
        3. Processes the formatted input using a language model (LLM).
        4. Parses the output into a structured string format.
        Returns:
            chain: A processing chain that takes a question as input and produces
                a context-aware response.
        """
        
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
        """
        Retrieve documents relevant to the given query.

        This method uses the retriever to fetch documents that are most similar
        or relevant to the input query.

        Args:
            query (str): The input query string for which relevant documents
                        need to be retrieved.

        Returns:
            list: A list of documents retrieved based on the query.
        """
    # return vector_store.similarity_search(query, k=5)
        return self.retriever.invoke(query)


    def serialize_docs(self, retrieved_docs):
        """
        Serializes a list of retrieved documents into a formatted string of sources.
        Args:
            retrieved_docs (list): A list of document objects, where each document contains
                metadata with at least a 'source' key. Optionally, documents may also have
                a 'page' key in their metadata.
        Returns:
            str: A formatted string listing the sources of the documents. Each source is
            prefixed with an asterisk (*) and includes the page number if available.
            The string begins with "Fuentes:\n".
        """
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
        """
        Retrieve and serialize documents based on the given query.
        This method first retrieves documents relevant to the provided query
        and then serializes them into a desired format.
        Args:
            query (str): The input query used to retrieve relevant documents.
        Returns:
            Any: The serialized representation of the retrieved documents.
        """

        retrieved_docs = self.get_retrieved_docs(query)
        sources = self.serialize_docs(retrieved_docs)
        return sources
    

    def invoke(self, query):
        """
        Processes a query by invoking the chain and retrieving associated sources.
        Args:
            query (str): The input query to be processed.
        Returns:
            str: The combined response from the chain and its associated sources,
                formatted as the chain's response followed by the sources.
        """

        response = self.chain.invoke(query)
        sources = self.get_sources(query)
        response_sources = response + "\n\n" + sources

        return response_sources