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
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=EXTRACTION_SYSTEM_MESSAGE),
            ("human", EXTRACTION_HUMAN_MESSAGE)
        ])

        json_parser = JsonOutputParser()

        extraction_chain = prompt | self.llm | json_parser

        return extraction_chain
    

    def build_dynamic_rag_chain(self, pdf_document):

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