from app.schemas.classification_state import ClassificationState
from app.graph.classification_nodes import (
    input_processor, hypothesis_generator, research_planner, internet_researcher,
    question_selector, hypothesis_updater, confidence_checker, final_output_provider
)
from langgraph.graph import StateGraph, END
from app.db.checkpointer import checkpointer



graph = StateGraph(ClassificationState)

graph.add_node("input_processor", input_processor)
graph.add_node("hypothesis_generator", hypothesis_generator)
graph.add_node("research_planner", research_planner)
graph.add_node("internet_researcher", internet_researcher)
graph.add_node("question_selector", question_selector)
graph.add_node("hypothesis_updater", hypothesis_updater)
graph.add_node("confidence_checker", confidence_checker)
graph.add_node("final_output_provider", final_output_provider)

graph.add_edge("input_processor", "hypothesis_generator")
graph.add_edge("hypothesis_generator", "research_planner")
graph.add_edge("research_planner", "internet_researcher")
graph.add_edge("internet_researcher", "question_selector")
graph.add_edge("question_selector", "hypothesis_updater")
graph.add_edge("hypothesis_updater", "confidence_checker")

def route_confidence(state: ClassificationState) -> str:
    return "final_output_provider" if state.confident else "research_planner"

graph.add_conditional_edges("confidence_checker", route_confidence, 
                            {"final_output_provider": "final_output_provider", 
                             "research_planner": "research_planner"})
graph.add_edge("final_output_provider", END)

graph.set_entry_point("input_processor")

ClassificationGraph = graph.compile(checkpointer=checkpointer, interrupt_before=['hypothesis_updater'])