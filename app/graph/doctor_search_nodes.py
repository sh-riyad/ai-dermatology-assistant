from app.services import llm
from app.schemas.doctor_search_state import DoctorSearchState
import re
import json
from app.core.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from langchain.prompts import ChatPromptTemplate
from langchain_community.agent_toolkits import create_sql_agent
from app.prompts.doctor_search import SCHEMA_ANALYZER_PROMPT, NLP_QUERY_PROMPT

def schema_analyzer(state: DoctorSearchState) -> DoctorSearchState:
    """Fetches schema and sample data from the database and generates questions."""
    
    # Get the actual database session from the generator.
    db_instance = next(get_db())
    
    # Use SQLAlchemy Inspector to fetch schema (columns information) for the 'doctors' table.
    inspector = inspect(db_instance.get_bind())
    columns_info = inspector.get_columns("doctors")
    columns = [col["name"] for col in columns_info]  # Extract the column names
    
    # Fetch sample data using a raw SQL query.
    sample_query = text("SELECT * FROM doctors LIMIT 3")
    sample_result = db_instance.execute(sample_query)
    sample_data = sample_result.fetchall()
    
    # Map each row to a dictionary using the column names.
    sample_data_dicts = [dict(zip(columns, row)) for row in sample_data]
    
    schema_str = ", ".join(columns)
    sample_data_str = json.dumps(sample_data_dicts, indent=2) if sample_data_dicts else "No sample data available."
    
    # Create the prompt using the schema information and sample data.
    prompt = ChatPromptTemplate.from_template(SCHEMA_ANALYZER_PROMPT).format(
        schema=schema_str, sample_data=sample_data_str
    )
    response = llm.invoke(prompt)
    
    # Parse the response into a list of questions.
    questions = response.content.split('\n')
    questions = [q.strip().lstrip('-').strip() for q in questions if q.strip()]
    
    state.questions = questions
    state.need_input = True
    
    return state


def query_generator_and_executor(state: DoctorSearchState) -> DoctorSearchState:
    """Generates a natural language query and executes it using the SQL agent."""
    
    db: Session = get_db()
    
    # Combine questions and answers for the prompt
    prompt = ChatPromptTemplate.from_template(NLP_QUERY_PROMPT).format(questions=state.questions, answers=state.answers)
    state.nlp_query = llm.invoke(prompt).content
    
    # Execute the query using the SQL agent
    sql_agent = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
    query_ans = sql_agent.invoke(state.nlp_query)

    state.final_ans = query_ans['output']
    return state