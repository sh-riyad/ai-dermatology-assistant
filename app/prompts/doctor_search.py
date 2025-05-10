SCHEMA_ANALYZER_PROMPT = """
You are an assistant helping users find doctors. The database has columns: {schema}. 
Sample data: {sample_data}. Generate a 3 questions to narrow down the search only based on the schema, Output just the questions.
specially dont as for names
"""

NLP_QUERY_PROMPT = """
Based on these questions and answers:
{questions} \n {answers}
Generate a natural language query like "Find me a doctor [conditions]". Just give me the query in string
"""