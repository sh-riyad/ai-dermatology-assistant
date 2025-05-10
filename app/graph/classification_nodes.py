from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.prompts.disease_classification import (
    HYPOTHESIS_PROMPT,
    HYPOTHESIS_UPDATE_PROMPT,
    QUESTION_SELECTOR_PROMPT,
    RESEARCH_PLAN_PROMPT,
    ANALYSE_IMAGE_PROMPT,
)
from app.services import llm, tavily
from app.schemas.classification_state import ClassificationState
from openai import OpenAI


def input_processor(state: ClassificationState) -> ClassificationState:
    """Processes initial user input if not already provided."""
    if state.encoded_image:
        client = OpenAI()
        completion = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": ANALYSE_IMAGE_PROMPT.format(
                                user_input=state.user_responses
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{state.encoded_image}",
                            },
                        },
                    ],
                }
            ],
            # max_tokens=1000
        )
        state.image_details = completion.choices[0].message.content
    return state


def hypothesis_generator(state: ClassificationState) -> ClassificationState:
    """Generates initial disease hypotheses."""
    prompt = HYPOTHESIS_PROMPT.format(
        description=state.input_description, image_details=state.image_details
    )
    response = llm.invoke(
        [
            SystemMessage(content="You are a dermatology assistant."),
            HumanMessage(content=prompt),
        ]
    )
    diseases = [d.strip() for d in response.content.split("\n") if d.strip()]

    state.current_hypotheses = [(disease, 1.0 / len(diseases)) for disease in diseases]
    return state


# def research_planner(state: State) -> State:
#     """Plans research using AI."""
#     diseases = ', '.join([disease for disease, _ in state['current_hypotheses']])
#     prompt = RESEARCH_PLAN_PROMPT.format(diseases=diseases)
#     response = llm.invoke([SystemMessage(content="You are a dermatology research assistant."),
#                           HumanMessage(content=prompt)])
#     queries = [q.strip() for q in response.content.split('\n') if q.strip()]
#     state['research_queries'] = queries
#     return state


def research_planner(state: ClassificationState) -> ClassificationState:
    """Plans internet research by generating searchable queries based on hypotheses."""
    hypotheses = [disease for disease, _ in state.current_hypotheses]
    queries = []
    for disease in hypotheses:
        queries.append(f"common symptoms of {disease} skin condition")
        # queries.append(f"causes of {disease} dermatology")
        # queries.append(f"diagnostic criteria for {disease} skin disease")
    state.research_queries = queries
    return state


def internet_researcher(state: ClassificationState) -> ClassificationState:
    """Conducts internet research."""
    findings = {}
    for query in state.research_queries:
        results = tavily.invoke({"query": query})
        findings[query] = results["results"][0]["content"]
    state.research_findings.update(findings)
    return state


def question_selector(state: ClassificationState) -> ClassificationState:
    """Selects a simple question using AI."""
    state.conversation_history.append(HumanMessage(content=state.input_description))
    history_text = "\n".join(
        [f"{msg.type}: {msg.content}" for msg in state.conversation_history]
    )
    findings_text = "\n".join([f"{q}: {f}" for q, f in state.research_findings.items()])
    prompt = (
        QUESTION_SELECTOR_PROMPT
        + f"\n\nResearch Findings:\n{findings_text}\n\nConversation History:\n{history_text}"
    )
    response = llm.invoke(
        [
            SystemMessage(content="You are a dermatology assistant."),
            HumanMessage(content=prompt),
        ]
    )
    state.current_question = response.content.strip()
    state.conversation_history.append(AIMessage(content=state.current_question))
    return state


def hypothesis_updater(state: ClassificationState) -> ClassificationState:
    """Updates hypotheses based on history."""
    history_text = "\n".join(
        [f"{msg.type}: {msg.content}" for msg in state.conversation_history]
    )
    prompt = (
        HYPOTHESIS_UPDATE_PROMPT
        + f"\n\nInitial Description: {state.input_description}\n\nConversation History:\n{history_text}"
    )
    response = llm.invoke(
        [
            SystemMessage(content="You are a dermatology assistant."),
            HumanMessage(content=prompt),
        ]
    )
    lines = response.content.split("\n")
    updated_hypotheses = []
    for line in lines:
        if ":" in line:
            parts = line.split(":")
            if len(parts) == 2:
                disease, prob = parts
                try:
                    updated_hypotheses.append((disease.strip(), float(prob.strip())))
                except ValueError:
                    continue
    state.current_hypotheses = (
        updated_hypotheses if updated_hypotheses else state.current_hypotheses
    )
    return state


def confidence_checker(state: ClassificationState) -> ClassificationState:
    """Checks confidence level."""
    state.iteration_count += 1
    if state.current_hypotheses:
        top_prob = max(prob for _, prob in state.current_hypotheses)
        if top_prob > 0.9 or state.iteration_count >= 3:
            state.confident = True
    return state


def final_output_provider(state: ClassificationState) -> ClassificationState:
    """Provides the final diagnosis."""
    if state.current_hypotheses:
        top_disease, top_prob = max(state.current_hypotheses, key=lambda x: x[1])
        print(f"Diagnosis: {top_disease} with {top_prob*100:.2f}% confidence.")
    else:
        print("Unable to determine a diagnosis.")
    return state
