
import os
from dotenv import load_dotenv


from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

from langgraph.graph import END, START, StateGraph
# from langgraph.checkpoint.memory import MemorySaver


from typing import TypedDict, Literal
from pydantic import BaseModel, Field

from src.rag_app.sql_retrieval import SQLRetrieval
from src.rag_app.chain import RAGChain
from src.rag_app.prompts import MULTI_AGENT_SYSTEM_PROMPT


class RouteQuery(BaseModel):
    """
    RouteQuery is a Pydantic model that represents the routing of a user query 
    to the most relevant data source. It includes the following attributes:

    Attributes:
        datasource (Literal["rag", "sql"]): Specifies the target data source 
            for the query. The value can either be "rag" (retrieval-augmented 
            generation) or "sql" (structured query language). This field is 
            required and includes a description to guide its usage.
    """
    datasource: Literal["rag", "sql"] = Field(
        ...,
        description="Dada una pregunta de usuario elige enrutarla a rag o a sql"
    )


class State(TypedDict):
    """
    State is a TypedDict that represents the structure of a state object.

    Attributes:
        query (str): The query string associated with the state.
        route (str): The route or path associated with the state.
        response (str): The response string associated with the state.
    """
    query: str
    route: str
    response: str


class MultiAgentGraph:
    """
    MultiAgentGraph is a class that orchestrates a multi-agent system for query routing and retrieval. 
    It integrates a Retrieval-Augmented Generation (RAG) chain, an SQL retrieval chain, and a 
    language model (LLM) to process and route queries to the appropriate data source.
    Methods:
    ---------
    - __init__():
        Initializes the MultiAgentGraph instance by setting up the RAG chain, SQL chain, LLM, 
        and building the state graph.
    - get_llm():
        Configures and returns an AzureChatOpenAI instance using environment variables for API 
        credentials and deployment details.
    - get_question_router():
        Creates and returns a question router that uses the LLM to determine the appropriate 
        data source (RAG or SQL) for a given query.
    - route_query(state: dict) -> str:
        Routes a query to the appropriate data source by invoking the question router. 
        Returns "rag" or "sql" based on the determined source.
    - rag_retriever(state: dict):
        Processes a query using the RAG chain and returns the response along with the query 
        and route information.
    - sql_retriever(state: dict):
        Processes a query using the SQL chain and returns the response along with the query 
        and route information.
    - build_graph():
        Constructs a state graph workflow that routes queries to the appropriate retriever 
        (RAG or SQL) based on the question router's decision. The graph is compiled and returned.
    - invoke(query: str):
        Executes the state graph with the provided query and returns the final response from 
        the appropriate retriever.
    Attributes:
    -----------
    - rag_chain: RAGChain
        An instance of the RAG chain for retrieval-augmented generation.
    - sql_chain: SQLRetrieval
        An instance of the SQL retrieval chain for querying structured data.
    - llm: AzureChatOpenAI
        The language model used for query routing and structured output generation.
    - graph: StateGraph
        The compiled state graph that orchestrates the query routing and retrieval process.
    """
    def __init__(self, type = "vanilla"):
        self.rag_chain = RAGChain()
        self.sql_chain = SQLRetrieval()
        self.llm = self.get_llm()

        if type == "vanilla":
            self.graph = self.build_graph()
        if type == "sqlbackup":
            self.graph = self.build_sqlbackup_graph()


    def get_llm(self):
        """
        Initializes and returns an AzureChatOpenAI instance configured with environment variables.
        This method loads the necessary environment variables to configure the Azure OpenAI API client.
        It retrieves the API key, endpoint, deployment name, and API version from the environment
        and uses them to create an instance of AzureChatOpenAI.
        Returns:
            AzureChatOpenAI: An instance of the AzureChatOpenAI client configured with the specified
            API key, endpoint, deployment name, and API version.
        Environment Variables:
            AZURE_OPENAI_API_KEY (str): The API key for authenticating with Azure OpenAI.
            AZURE_OPENAI_ENDPOINT (str): The base URL of the Azure OpenAI endpoint.
            03_MINI_DEPLOYMENT (str): The name of the deployment to use (not the model name).
            AZURE_OPENAI_API_VERSION (str): The version of the Azure OpenAI API to use.
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

    
    def get_question_router(self):
        """
        Creates and returns a question router for handling queries.
        The question router is constructed by combining a chat prompt template
        with a structured output LLM (Language Model) router. The chat prompt
        template defines the interaction format using system and human messages,
        while the structured LLM router ensures the output adheres to the
        specified structure.
        Returns:
            Callable: A question router that processes queries and routes them
            based on the defined prompt and structured output.
        """
        structured_llm_router = self.llm.with_structured_output(RouteQuery)
        route_prompt = ChatPromptTemplate.from_messages(
            messages=[
                ("system", MULTI_AGENT_SYSTEM_PROMPT),
                ("human", "{query}")
            ]
        )

        question_router = route_prompt | structured_llm_router

        return question_router


    def route_query(self, state) -> str:
        """
        Routes a query to the appropriate data source based on the provided state.
        Args:
            state (dict): A dictionary containing the query information. 
                        It must include a "query" key with the query string.
        Returns:
            str: A string indicating the data source to use. 
                Possible values are "rag" or "sql".
        Raises:
            ValueError: If the data source returned by the question router is unknown.
        """
        
        query = state["query"]
        question_router = self.get_question_router()
        source = question_router.invoke({"query": query})

        if source.datasource == "rag":
            return "rag"
        elif source.datasource == "sql":
            return "sql"
        else:
            raise ValueError(f"Unknown source: {source['datasource']}")


    def rag_retriever(self, state):
        """
        Handles the retrieval process using a Retrieval-Augmented Generation (RAG) chain.
        Args:
            state (dict): A dictionary containing the input state. It must include the key "query",
                        which represents the input query string.
        Returns:
            dict: A dictionary containing:
                - "query" (str): The original input query.
                - "route" (str): A string indicating the route, in this case, "rag".
                - "response" (Any): The response generated by the RAG chain based on the input query.
        """

        query = state["query"]
        response = self.rag_chain.invoke(query)
        return {"query": query, "route": "rag", "response": response}


    def sql_retriever(self, state):
        """
        Executes a SQL query using the provided state and retrieves the response.

        Args:
            state (dict): A dictionary containing the query to be executed. 
                        Expected key:
                        - "query" (str): The SQL query string to be executed.

        Returns:
            dict: A dictionary containing:
                - "query" (str): The original SQL query.
                - "route" (str): The route identifier, set to "sql".
                - "response" (Any): The response obtained from executing the SQL query.
        """
        query = state["query"]
        response = self.sql_chain.invoke(query)
        return {"query": query, "route": "sql", "response": response}


    def build_graph(self):
        """
        Builds and compiles a state graph workflow for query routing and processing.
        The method creates a `StateGraph` instance and defines nodes and edges
        to represent the workflow. It includes two retriever nodes ("rag" and "sql")
        and conditional logic to route queries based on the `route_query` function.
        The workflow is compiled into a graph structure and returned.
        Returns:
            graph: The compiled state graph representing the workflow.
        """

        workflow = StateGraph(State)

        workflow.add_node("rag", self.rag_retriever)
        workflow.add_node("sql", self.sql_retriever)
        workflow.add_conditional_edges(
            START,
            self.route_query, 
            {
                "rag": "rag",
                "sql": "sql"
            }
        )

        workflow.add_edge("rag", END)
        workflow.add_edge("sql", END)

        # memory = MemorySaver()  # Crear una instancia de MemorySaver
        # workflow.enable_memory(memory)  # Habilitar la memoria en el grafo

        graph = workflow.compile()

        return graph
    

    def build_sqlbackup_graph(self):
        """
        Builds and compiles a state graph workflow for query routing and processing.
        The method creates a `StateGraph` instance and defines nodes and edges
        to represent the workflow. It includes two retriever nodes ("rag" and "sql")
        and conditional logic to route queries based on the `route_query` function.
        If the SQL retriever does not find information, the query is routed to the RAG retriever.
        Returns:
            graph: The compiled state graph representing the workflow.
        """

        workflow = StateGraph(State)

        # Add nodes for RAG and SQL retrievers
        workflow.add_node("rag", self.rag_retriever)
        workflow.add_node("sql", self.sql_retriever)

        # Add conditional logic to route queries based on the question router
        workflow.add_conditional_edges(
            START,
            self.route_query,
            {
                "rag": "rag",
                "sql": "sql"
            }
        )

        # Add conditional logic to check SQL response using LLM
        def check_sql_response(state):
            """
            Checks if the SQL retriever found relevant information by invoking the LLM.
            If the LLM determines the response is not relevant, routes the query to the RAG retriever.
            """
            response = state["response"]
            query = state["query"]

            # Use LLM to evaluate the relevance of the SQL response
            llm_prompt = f"Is the following response relevant to the query? Query: {query} Response: {response}. Answer with 'yes' or 'no'."
            llm_response = self.llm.invoke({"query": llm_prompt})

            if llm_response.strip().lower() == "no":
                return "rag"
            else:
                return END

        # Add edges for SQL fallback to RAG
        workflow.add_conditional_edges(
            "sql",
            check_sql_response,
            {
                "rag": "rag",
                END: END
            }
        )

        # Add direct edge from RAG to END
        workflow.add_edge("rag", END)

        # Compile the graph
        graph = workflow.compile()

        return graph


    def invoke(self, query):
        """
        Executes a query on the graph and retrieves the response.
        Args:
            query (str): The query string to be executed on the graph.
        Returns:
            str: The response obtained from the graph execution.
        """
        """"""
        response = self.graph.invoke({"query": query})

        # return response["response"]
        return response
