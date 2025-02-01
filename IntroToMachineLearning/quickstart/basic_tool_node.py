import json
from typing import cast
from langchain_core.messages import ToolMessage, AIMessage

TOOLS_NODE_NAME = "tools"

class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        # Constructs a dictionary of tool names mapped to tools
        self.tools_by_name = {
            tool.name: tool for tool in tools
        }

    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = cast(AIMessage, messages[-1])

            outputs = []
            for tool_call in message.tool_calls:
                tool_result = self.tools_by_name[tool_call["name"]].invoke(
                    tool_call["args"]
                )
                outputs.append(
                    ToolMessage(
                        # serialize
                        content = json.dumps(tool_result),
                        name = tool_call["name"],
                        tool_call_id = tool_call["id"]
                    )
                )

            return { "messages": outputs }
        else:
            raise ValueError("No messages found in input")

from quickstart.state import State
def route_tools(state: State) -> str:
    """
    Use in the conditional_edge to route to the ToolNode if the
    last message has tool calls. Otherwise, route to the end.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []): # it's a dict
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")

    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return TOOLS_NODE_NAME # CODE SMELL; this is the name of the node!

    from langgraph.graph import END
    return END
