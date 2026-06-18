"""Prompt templates for the agent nodes.

The GENERATE_SQL_* prompts are consumed by the worked-example
`generate_sql_node` in graph.py via `.format(schema=..., question=...)`, so
keep those placeholders intact. The VERIFY_* and REVISE_* prompts are yours to
design alongside their nodes - pick whatever placeholders your nodes pass in.

Filling these in is part of Phase 3.
"""

GENERATE_SQL_SYSTEM = """You are a master SQL developer. Your task is to write a SQLite query that answers the user's
question based on the provided database schema.
Return only the raw SQL query string. Do not include markdown code blocks, backticks, or explanations.
Ensure the query is valid SQLite and uses the correct table and column names from the schema."""

# Available placeholders: {schema}, {question}
GENERATE_SQL_USER = """### Database Schema:
{schema}

### Question:
{question}

### SQL Query:"""


VERIFY_SYSTEM = """You are a SQL output verifier. Your task is to determine if the execution results of a SQL query
plausibly answer the user's question.
You will be given the question, the SQL query, and the execution results.

Consider:
1. If there is an error (e.g., SQLite error), it is NOT plausible.
2. If 0 rows are returned but the question implies data should exist (e.g., "List all...", "What is..."), it might be an issue. However, if the question asks "how many" and the count is 0, that's fine.
3. If the columns returned do not seem to answer the question (e.g., the user asked for names but you got IDs).
4. If the data returned looks like a placeholder or obviously wrong (e.g., coordinates that are 0,0).

Output your decision in JSON format:
{"ok": true, "issue": null} or {"ok": false, "issue": "A detailed description of the problem"}
"""

VERIFY_USER = """### Question:
{question}

### SQL Query:
{sql}

### Execution Result:
{result}

### Decision (JSON):"""


REVISE_SYSTEM = """You are a SQL expert optimising a failing query. Your task is to fix a SQL query that failed verification.
You will be given the original question, the schema, the failing SQL, the execution result, and the reason it failed.

Your goal is to produce a corrected SQLite query that addresses the issue.
Return ONLY the raw executable SQL query string. Do not include markdown code blocks, backticks, or explanations.
"""

REVISE_USER = """### Database Schema:
{schema}

### Question:
{question}

### Failing SQL:
{sql}

### Execution Result:
{result}

### Issue Found:
{issue}

### Corrected SQL Query:"""
