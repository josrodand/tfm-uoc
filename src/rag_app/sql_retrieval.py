import os
from dotenv import load_dotenv

from langchain_community.utilities import SQLDatabase
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import AzureChatOpenAI


from src.processing.params import ( 
    RAG_DATA_PATH, 
    SQLITE_DATA_PATH, 
    SQLITE_FILE_NAME
)

class SQLRetrieval:
    def __init__(self, verbose=False):
        self.sqlite_path = f"{RAG_DATA_PATH}/{SQLITE_DATA_PATH}/{SQLITE_FILE_NAME}"
        self.uri = f"sqlite:///{self.sqlite_path}"
        self.llm = self.get_llm()
        self.verbose=verbose
        self.sql_agent = self.build_sql_agent()
        


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
    

    def build_sql_agent(self):

        db = SQLDatabase.from_uri(self.uri)
        toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
        agent_executor = create_sql_agent(llm=self.llm, toolkit=toolkit, verbose=self.verbose)

        return agent_executor
    

    def invoke(self, query):
        response = self.sql_agent.invoke(query)
        return response['output']
