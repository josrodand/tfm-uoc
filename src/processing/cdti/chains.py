import os
from dotenv import load_dotenv

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import AzureChatOpenAI
from langchain_openai import AzureOpenAIEmbeddings


from src.processing.cdti.prompts import (
    EXTRACTION_SYSTEM_MESSAGE,
    EXTRACTION_HUMAN_MESSAGE,
    DYNAMIC_RAG_PROMPT_TEMPLATE
)

class CDTIChainBuilder:
    """
    CDTIChainBuilder is a utility class designed to build and manage chains for processing and extracting information 
    using Azure OpenAI services. It provides methods to create specific chains for data extraction and dynamic 
    retrieval-augmented generation (RAG) tasks.
    Attributes:
        llm (AzureChatOpenAI): An instance of AzureChatOpenAI configured with the provided API key, endpoint, 
            deployment name, and API version.
        embeddings (AzureOpenAIEmbeddings): An instance of AzureOpenAIEmbeddings used for generating embeddings 
            for text documents.
    Methods:
        build_extraction_chain():
            Constructs a chain for extracting structured information from input data. The chain uses a prompt 
            template, an Azure OpenAI language model, and a JSON output parser to process the input and return 
            extracted data in JSON format.
        build_dynamic_rag_chain(pdf_document):
            Constructs a dynamic retrieval-augmented generation (RAG) chain for processing a PDF document. The 
            method splits the document into chunks, generates embeddings, stores them in a vector store, and 
            retrieves relevant chunks for answering questions. The chain uses a prompt template, an Azure OpenAI 
            language model, and a string output parser to generate responses.
            Args:
                pdf_document: The input PDF document to be processed and split into chunks.
            Returns:
                A dynamic RAG chain configured to retrieve context and generate responses based on the input 
                document.
    """

    def __init__(self):

        load_dotenv()

        api_key = os.getenv("AZURE_OPENAI_API_KEY")
        api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment = os.getenv("03_MINI_DEPLOYMENT")  # nombre del *deployment*, NO del modelo
        api_version = os.getenv("AZURE_OPENAI_API_VERSION")  # Ajusta según la versión de tu Azure OpenAI

        self.llm = AzureChatOpenAI(
            openai_api_key=api_key,
            azure_endpoint=api_base,
            deployment_name=deployment,
            api_version=api_version,
            # temperature=0
        )

        self.embeddings = AzureOpenAIEmbeddings(
            model="text-embedding-3-large",
            azure_endpoint=api_base,
            api_key=api_key,
            openai_api_version=api_version
        )


    def build_extraction_chain(self):
        """
        Builds an extraction chain for processing input data.
        This method constructs a chain of operations that includes:
        1. A chat prompt template initialized with system and human messages.
        2. A JSON output parser for parsing the output.
        3. A language model (LLM) integrated into the chain.
        The chain is created by combining the prompt, the LLM, and the JSON parser
        in sequence, enabling structured data extraction from input.
        Returns:
            The constructed extraction chain.
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=EXTRACTION_SYSTEM_MESSAGE),
            ("human", EXTRACTION_HUMAN_MESSAGE)
        ])

        json_parser = JsonOutputParser()

        extraction_chain = prompt | self.llm | json_parser

        return extraction_chain
    

    def build_dynamic_rag_chain(self, pdf_document):
        """
        Builds a dynamic Retrieval-Augmented Generation (RAG) chain for processing a PDF document.
        This method splits the input PDF document into chunks, creates a vector store for the chunks
        using embeddings, and sets up a retriever for similarity-based search. It then constructs a 
        RAG chain using a prompt template and a language model.
        Args:
            pdf_document (Document): The input PDF document to be processed.
        Returns:
            Callable: A RAG chain that processes input questions using the context retrieved from the
            vector store and generates responses using the language model.
        """

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(pdf_document)

        #chroma
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings
        )

        retriever = vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )

        prompt = ChatPromptTemplate.from_template(DYNAMIC_RAG_PROMPT_TEMPLATE)

        rag_chain = (
            {"context": retriever,
            "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        return rag_chain