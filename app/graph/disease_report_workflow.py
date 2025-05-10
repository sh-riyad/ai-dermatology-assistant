from langgraph.graph import StateGraph, END
from app.schemas.disease_report_state import ReportState
from app.graph.disease_report_nodes import (
    plan_node, research_plan_node, reflection_node,
    generation_node, research_critique_node,
    should_continue
)

builder = StateGraph(ReportState)

builder.add_node("planner", plan_node)
builder.add_node("research_plan", research_plan_node)
builder.add_node("generate", generation_node)
builder.add_node("reflect", reflection_node)
builder.add_node("research_critique", research_critique_node)

builder.set_entry_point("planner")
builder.add_edge("planner", "research_plan")
builder.add_edge("research_plan", "generate")
builder.add_conditional_edges("generate", should_continue, {END: END, "reflect": "reflect"})
builder.add_edge("reflect", "research_critique")
builder.add_edge("research_critique", "generate")

disease_report_graph = builder.compile()