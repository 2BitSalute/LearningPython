import os

from quickstart import graph

def stream_graph_updates(user_input: str):
    # Dirty, dirty.
    # Config is required by the graph if it were built with a checkpointer,
    # But this detail leaks out here, where you might not know how
    # the graph was compiled.
    for event in graph.stream(
        input = {
            "messages": [{
                    "role": "user",
                    "content": user_input
                }
            ]
        },
        config = {
            "configurable": {
                "thread_id": 1
            }
        }):
        for value in event.values():
            # Prints the last message (what is before that?)
            print("Assistant: ", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break

        # Messages are appended?
        stream_graph_updates(user_input)
    except:
        # fall back if input() is not available
        user_input = "Help me plan a spring for my team"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break # Only one turn?