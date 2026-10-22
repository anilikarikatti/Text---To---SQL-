from langgraph.graph import StateGraph, START, END

from app.graph_state import TextToSQLState
from app.graph_nodes import (
    generate_sql_node,
    validate_sql_node,
    execute_sql_node,
)


from app.graph_nodes import MAX_ATTEMPTS


def route_after_execution(state: dict) -> str:
    # No database error: return the results.
    if state.get("error") is None:
        return "done"

    # Stop after the maximum number of SQL generations.
    if state["attempts"] >= MAX_ATTEMPTS:
        return "done"

    # Database error: try generating corrected SQL.
    return "retry"



builder = StateGraph(TextToSQLState)

builder.add_node("generate_sql", generate_sql_node)
builder.add_node("validate_sql", validate_sql_node)
builder.add_node("execute_sql", execute_sql_node)

builder.add_edge(START, "generate_sql")
builder.add_edge("generate_sql", "validate_sql")
builder.add_edge("validate_sql", "execute_sql")

builder.add_conditional_edges(
    "execute_sql",
    route_after_execution,
    {
        "retry": "generate_sql",
        "done": END,
    },
)

text_to_sql_graph = builder.compile()