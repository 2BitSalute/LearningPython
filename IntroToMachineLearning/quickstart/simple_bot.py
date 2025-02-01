from langgraph.graph import StateGraph, START, END

from .state import State

print("Annotations:")

for k, v in State.__annotations__.items():
    print(f"{k}: {v}")

graph_builder = StateGraph(state_schema=State)

def _set_env(var: str):
    keys = {
        "ANTHROPIC_API_KEY": "anthropic-key",
        "TAVILY_API_KEY": "tavily-key",
        "AZURE_OPENAI_API_KEY": "azure-openai-key",
        "AZURE_OPENAI_ENDPOINT": "azure-openai-endpoint",
        "LANGSMITH_API_KEY": "langsmith-key"
    }

    import os

    print(os.getcwd())

    if not os.environ.get(var):
        with open(f"secrets/{keys[var]}", "r") as anthropic_key:
            os.environ[var] = anthropic_key.read()
        # This is silly and annoying
        # os.environ[var] = getpass.getpass(f"{var}: ")

from langchain_community.tools.tavily_search import TavilySearchResults

_set_env("TAVILY_API_KEY")
tools = [
    TavilySearchResults(max_results = 2)
]

# Anthropic pricing:
# https://www.anthropic.com/pricing#anthropic-api

_set_env("ANTHROPIC_API_KEY")

from langchain_anthropic import ChatAnthropic

# Supported models:
# https://docs.anthropic.com/en/docs/build-with-claude/batch-processing#supported-models
# cheapest
# claude-3-haiku-20240307
anthropicLLM = ChatAnthropic(
    model="claude-3-haiku-20240307").bind_tools(tools)

def anthropic_chatbot(state: State) -> State:
    print()
    print("in anthropic_chatbot")
    print(state["messages"])
    print()
    print()

    # Returns a new state
    return { "messages": [anthropicLLM.invoke(state["messages"])]}

# TODO: replace Anthropic with OpenAI or with azure?
# See docs about instantiation: https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.azure.AzureChatOpenAI.html#langchain_openai.chat_models.azure.AzureChatOpenAI
# from langchain_openai import ChatOpenAI
# ChatOpenAI()

chatbot_node_name = f"Chatbot-{anthropicLLM.model}"
chatbot_function = anthropic_chatbot

graph_builder.add_node(
    chatbot_node_name,
    chatbot_function
)

from .basic_tool_node import (
    BasicToolNode,
    TOOLS_NODE_NAME,
    route_tools
)

graph_builder.add_node(TOOLS_NODE_NAME, BasicToolNode(tools))
graph_builder.add_conditional_edges(
    chatbot_node_name,
    route_tools,
    {
        "tools": TOOLS_NODE_NAME,
        END: END
    }
)

graph_builder.add_edge(
    TOOLS_NODE_NAME,
    chatbot_node_name
)

graph_builder.add_edge(
    START,
    chatbot_node_name
)


# Without a checkpointer, the graph restarts each time,
# meaning that no history is preserved.
# This is quite interesting. The docs say to not use MemorySaver for
# production. That's really strange.
from langgraph.checkpoint.memory import MemorySaver

graph = graph_builder.compile(checkpointer=MemorySaver())
