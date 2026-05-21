from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

load_dotenv()

_agent = None

def get_agent():
    global _agent
    if _agent == None:


        db = SQLDatabase.from_uri(os.getenv("DB_URL"), include_tables = ["core_batting", "core_bowling", "core_fielding"], sample_rows_in_table_info=1)


        llm = ChatGroq(api_key=os.getenv("PRIMARY_API_KEY"), model="openai/gpt-oss-120b")

        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        tools = toolkit.get_tools()

        memory = MemorySaver()

        _agent = create_agent(model=llm, checkpointer=memory, tools=tools, system_prompt="""You are CricketQL, a cricket data assistant.
For greetings or non-data questions, respond immediately without using any tools.
Only use tools when the user asks for specific cricket statistics or data.
Always filter NULL values in queries.
Always use ORDER BY when ranking.""")
    
    return _agent