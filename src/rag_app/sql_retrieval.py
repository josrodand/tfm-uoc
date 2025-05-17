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
    """
    A class to handle SQL-based retrieval using a language model and an SQLite database.
    Attributes:
        sqlite_path (str): The path to the SQLite database file.
        uri (str): The URI for the SQLite database.
        llm (AzureChatOpenAI): The language model used for SQL query generation and execution.
        verbose (bool): Flag to enable verbose output for debugging.
        sql_agent (AgentExecutor): The SQL agent responsible for executing queries.
    Methods:
        __init__(verbose=False):
            Initializes the SQLRetrieval instance, setting up the database path, URI, 
            language model, and SQL agent.
        get_llm():
            Loads environment variables and initializes the AzureChatOpenAI language model.
        build_sql_agent():
            Creates and configures the SQL agent using the language model and database toolkit.
        invoke(query):
            Executes a SQL query using the SQL agent and returns the result.
    """
    def __init__(self, verbose=False):
        self.sqlite_path = f"{RAG_DATA_PATH}/{SQLITE_DATA_PATH}/{SQLITE_FILE_NAME}"
        self.uri = f"sqlite:///{self.sqlite_path}"
        self.llm = self.get_llm()
        self.verbose=verbose
        self.sql_agent = self.build_sql_agent()
        


    def get_llm(self):
        """
        Initializes and returns an AzureChatOpenAI instance configured with environment variables.
        This method loads environment variables using `load_dotenv()` and retrieves the necessary
        configuration values for connecting to an Azure OpenAI deployment. These include the API key,
        endpoint, deployment name, and API version. The AzureChatOpenAI instance is then created
        with these parameters.
        Returns:
            AzureChatOpenAI: An instance of AzureChatOpenAI configured with the specified environment variables.
        Environment Variables:
            AZURE_OPENAI_API_KEY (str): The API key for authenticating with Azure OpenAI.
            AZURE_OPENAI_ENDPOINT (str): The base URL of the Azure OpenAI endpoint.
            03_MINI_DEPLOYMENT (str): The name of the Azure OpenAI deployment (not the model name).
            AZURE_OPENAI_API_VERSION (str): The API version to use with Azure OpenAI.
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
    

    def build_sql_agent(self):
        """
        Builds and returns an SQL agent executor.
        This method initializes an SQL database connection using the provided URI,
        creates a toolkit for interacting with the database using the specified
        language model (LLM), and constructs an SQL agent executor with the given
        configurations.
        Returns:
            AgentExecutor: An instance of the SQL agent executor configured with
            the database and language model.
        """

        db = SQLDatabase.from_uri(self.uri)
        toolkit = SQLDatabaseToolkit(db=db, llm=self.llm)
        agent_executor = create_sql_agent(llm=self.llm, toolkit=toolkit, verbose=self.verbose)

        return agent_executor
    

    def invoke(self, query):
        """
        Executes a SQL query using the SQL agent and returns the output.

        Args:
            query (str): The SQL query to be executed.

        Returns:
            str: The output of the executed SQL query.
        """
        response = self.sql_agent.invoke(query)
        return response['output']
