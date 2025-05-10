from app.prompts.disease_report_prompts import PLAN_PROMPT, RESEARCH_PLAN_PROMPT, WRITER_PROMPT, RESEARCH_CRITIQUE_PROMPT, REFLECTION_PROMPT
from app.schemas.disease_report_state  import ReportState, Queries
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.services import llm, tavily
from langgraph.graph import END

def plan_node(state: ReportState):
    """Outline the approach for covering the user’s question."""
    messages = [
        SystemMessage(content=PLAN_PROMPT),
        HumanMessage(content=f"User request: {state.task}\n\nDetail level: {state.detail_level}\nLanguage: {state.language_preference}")
    ]
    response = llm.invoke(messages)
    return {"plan": response.content}


def research_plan_node(state: ReportState):
    """Come up with initial research queries, then fetch info from Tavily (or any data source)."""
    queries_resp = llm.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_PLAN_PROMPT),
        HumanMessage(content=state.task)
    ])
    content_list = state.content if state.content is not None else []

    for q in queries_resp.queries:
        search_result = tavily.invoke({"query": q})
        for r in search_result['results']:
            content_list.append(r['content'])

    return {"content": content_list}

def generation_node(state: ReportState):
    """Generate a structured draft with disclaimers, references, user language preference, etc."""
    content_str = "\n\n".join(state.content or [])
    user_message = HumanMessage(
        content=(
            f"Task: {state.task}\n"
            f"Plan:\n{state.plan}\n"
            f"Detail level: {state.detail_level}\n"
            f"Language: {state.language_preference}\n"
            f"Disclaimers: {state.disclaimers}"
        )
    )

    messages = [
        SystemMessage(content=WRITER_PROMPT.format(content=content_str)),
        user_message
    ]
    response = llm.invoke(messages)

    revision_number = state.revision_number if state.revision_number is not None else 1
    return {
        "draft": response.content,
        "revision_number": revision_number + 1
    }


def reflection_node(state: ReportState):
    """Review the draft and generate critique or improvement notes."""
    messages = [
        SystemMessage(content=REFLECTION_PROMPT),
        HumanMessage(content=state.draft)
    ]
    response = llm.invoke(messages)
    return {"critique": response.content}

def research_critique_node(state: ReportState):
    """If the reflection says something is missing, do new queries to fill in gaps."""
    queries_resp = llm.with_structured_output(Queries).invoke([
        SystemMessage(content=RESEARCH_CRITIQUE_PROMPT),
        HumanMessage(content=state.critique)
    ])

    content_list = state.content if state.content is not None else []
    for q in queries_resp.queries:
        search_result = tavily.invoke({"query": q})
        for r in search_result['results']:
            content_list.append(r['content'])

    return {"content": content_list}


def should_continue(state: ReportState):
    """Stop if we've hit the max revisions, otherwise go back to reflection."""
    if state.revision_number > state.max_revisions:
        return END
    return "reflect"

