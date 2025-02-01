from typing import Annotated
from typing_extensions import TypedDict

import langgraph.graph.message as message

class State(TypedDict):
    # Messages is a state key (and a key of TypedDict)
    # Messages have the type list
    # The add_messages function defines the update behavior
    # The behavior is append (vs. overwrite)
    messages: Annotated[list, message.add_messages]
