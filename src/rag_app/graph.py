
import os
from dotenv import load_dotenv


from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import AzureChatOpenAI

from langgraph.graph import END, START, StateGraph

from typing import TypedDict, Literal
from pydantic import BaseModel, Field

from src.rag_app.sql_retrieval import SQLRetrieval
from src.rag_app.chain import RAGChain
from src.rag_app.prompts import MULTI_AGENT_SYSTEM_PROMPT


class RouteQuery(BaseModel):
    """Enruta la query de usuario para la fuente de datos mas relevante."""
    datasource: Literal["rag", "sql"] = Field(
        ...,
        description="Dada una pregunta de usuario elige enrutarla a rag o a sql"
    )


class State(TypedDict):
    query: str
    route: str
    response: str


class MultiAgentGraph:
    def __init__(self):
        self.rag_chain = RAGChain()
        self.sql_chain = SQLRetrieval()
        self.llm = self.get_llm()
        self.graph = self.build_graph()


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

    
    def get_question_router(self):

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
        """"""
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

        """
        query = state["query"]
        response = self.rag_chain.invoke(query)
        return {"query": query, "route": "rag", "response": response}


    def sql_retriever(self, state):
        """"""
        query = state["query"]
        response = self.sql_chain.invoke(query)
        return {"query": query, "route": "sql", "response": response}


    def build_graph(self):
        """"""
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

        graph = workflow.compile()

        return graph


    def invoke(self, query):
        """"""
        response = self.graph.invoke({"query": query})

        return response["response"]

