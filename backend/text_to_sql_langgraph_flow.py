import sqlite3
from typing import TypedDict, Optional, List, Dict
from langgraph.graph import StateGraph, END

from backend.config import DB_PATH
from backend.translation import translate_to_english
from backend.sql_validator import validate_user_input, validate_sql
from backend.llm_connector import openrouter_chat
from backend.role_access import apply_role_based_filter
from backend.table_formatter import format_table
from backend.user_db import get_cached_result, store_cached_result


class GraphState(TypedDict):
    user_input: str
    role: str
    user_id: Optional[int]
    translated_input: Optional[str]
    sql_query: Optional[str]
    raw_data: Optional[List[Dict]]
    filtered_data: Optional[List[Dict]]
    final_result: Optional[Dict]


def execute_sql(sql):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def translate_node(state):
    state["translated_input"] = translate_to_english(
        validate_user_input(state["user_input"])
    )
    return state


#def llm_sql_node(state):
    #messages = [
        #{"role": "system", "content": "Generate ONE safe SELECT query only."},
        #{"role": "user", "content": state["translated_input"]}
    #]
   # state["sql_query"] = validate_sql(openrouter_chat(messages))
   # return state


def llm_sql_node(state):
    schema_context = """
You are an expert SQLite Text-to-SQL generator.

DATABASE SCHEMA:

TABLE employees:
- emp_id (INTEGER)          -- employee id
- emp_name (TEXT)           -- employee name
- dept_id (INTEGER)         -- department id
- salary (INTEGER)

TABLE departments:
- dept_id (INTEGER)
- dept_name (TEXT)

CRITICAL COLUMN MAPPINGS:
- "name", "employee name", "person", "staff name" → emp_name
- "id", "employee id", "emp id" → emp_id
- "department", "dept", "team" → dept_id

MANDATORY SQL RULES:
- ALWAYS use emp_name for names (never use 'name')
- ALWAYS use emp_id for IDs (never invent columns)
- NEVER use '=' for name matching
- ALWAYS use:
    emp_name LIKE '%value%' COLLATE NOCASE
- Use dept_id for department filtering (not dept_name unless explicitly asked)
- Generate ONLY ONE SQLite SELECT query
- NO explanations
- NO comments
- NO markdown
- Output ONLY valid SQL

INVALID EXAMPLES (DO NOT DO):
- WHERE name = 'SANGU'
- WHERE emp_name = 'SANGU'

VALID EXAMPLE:
- WHERE emp_name LIKE '%SANGU%' COLLATE NOCASE
"""

    messages = [
        {"role": "system", "content": schema_context},
        {"role": "user", "content": state["translated_input"]}
    ]

    sql_text = openrouter_chat(messages)
    state["sql_query"] = validate_sql(sql_text)
    return state



def execution_node(state):
    cached = get_cached_result(state["sql_query"])
    data = cached if cached else execute_sql(state["sql_query"])
    if not cached:
        store_cached_result(state["sql_query"], data)
    state["raw_data"] = data
    return state


def role_filter_node(state):
    state["filtered_data"] = apply_role_based_filter(
        state["raw_data"], state["role"], state["user_id"]
    )
    return state


def format_node(state):
    state["final_result"] = {
        "query": state["sql_query"],
        "result": format_table(state["filtered_data"])
    }
    return state


graph = StateGraph(GraphState)
graph.add_node("translate", translate_node)
graph.add_node("llm", llm_sql_node)
graph.add_node("execute", execution_node)
graph.add_node("filter", role_filter_node)
graph.add_node("format", format_node)

graph.set_entry_point("translate")
graph.add_edge("translate", "llm")
graph.add_edge("llm", "execute")
graph.add_edge("execute", "filter")
graph.add_edge("filter", "format")
graph.add_edge("format", END)

app = graph.compile()


def run_text_to_sql(user_input, role, user_id=None):
    state = {
        "user_input": user_input,
        "role": role,
        "user_id": user_id,
        "translated_input": None,
        "sql_query": None,
        "raw_data": None,
        "filtered_data": None,
        "final_result": None
    }
    return app.invoke(state)["final_result"]
