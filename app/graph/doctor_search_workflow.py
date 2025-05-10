from langgraph.graph import StateGraph, END
from app.graph.doctor_search_nodes import schema_analyzer, query_generator_and_executor
from app.schemas.doctor_search_state import DoctorSearchState
from app.db.checkpointer import checkpointer

graph = StateGraph(DoctorSearchState)
graph.add_node("schema_analyzer", schema_analyzer)
graph.add_node("query_generator_and_executor", query_generator_and_executor)

# Define the flow
graph.add_edge("schema_analyzer", "query_generator_and_executor")
graph.add_edge("query_generator_and_executor", END)

graph.set_entry_point("schema_analyzer")
DoctorSearchGraph = graph.compile(checkpointer=checkpointer, interrupt_before=["query_generator_and_executor"])