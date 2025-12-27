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


# =========================
# GRAPH STATE
# =========================
class GraphState(TypedDict):
    user_input: str
    role: str
    user_id: Optional[int]
    translated_input: Optional[str]
    sql_query: Optional[str]
    raw_data: Optional[List[Dict]]
    filtered_data: Optional[List[Dict]]
    final_result: Optional[Dict]
    sql_explanation: Optional[str]
    user_approval: Optional[bool]


# =========================
# DB EXECUTION
# =========================
def execute_sql(sql):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# =========================
# NODES
# =========================
def translate_node(state: GraphState):
    state["translated_input"] = translate_to_english(
        validate_user_input(state["user_input"])
    )
    return state
def llm_sql_node(state):
    schema_context = """
You are an expert SQLite Text-to-SQL generator.

DATABASE SCHEMA:

TABLE employees:
- emp_id (INTEGER)
- emp_name (TEXT)
- dept_id (INTEGER)
- salary (INTEGER)

TABLE departments:
- dept_id (INTEGER)
- dept_name (TEXT)

COLUMN MAPPINGS:
- name / employee name → emp_name
- id / employee id → emp_id
- department / team → dept_id

RULES:
- ALWAYS include emp_id in SELECT for internal processing (RBAC)
- Generate ONLY ONE SELECT query
- NEVER generate DELETE, UPDATE, INSERT, DROP
- NEVER use '=' for names
- ALWAYS use:
  emp_name LIKE '%value%' COLLATE NOCASE
- Output ONLY SQL (no explanation, no markdown)
"""

    messages = [
        {"role": "system", "content": schema_context},
        {"role": "user", "content": state["translated_input"]}
    ]

    sql_text = openrouter_chat(messages)

    # Ensure emp_id is included internally
    if "emp_id" not in sql_text.lower():
        sql_text = sql_text.replace("SELECT", "SELECT emp_id,", 1)

    state["sql_query"] = validate_sql(sql_text)
    return state




def explain_sql_node(state: GraphState):
    messages = [
        {
            "role": "system",
            "content": "Explain this SQL query in ONE simple sentence for a non-technical user."
        },
        {
            "role": "user",
            "content": state["sql_query"]
        }
    ]
    state["sql_explanation"] = openrouter_chat(messages)
    return state


def approval_node(state: GraphState):
    """
    Ask user whether to execute the query.
    """
    print("\nGenerated SQL Query:")
    print(state["sql_query"])
    print("\nExplanation for you:")
    print(state["sql_explanation"])
    ans = input("\nDo you want to execute this query? (yes/no): ").strip().lower()
    state["user_approval"] = ans in {"yes", "y"}
    return state


def execution_node(state: GraphState):
    if not state["user_approval"]:
        print("Query execution cancelled by user.")
        state["raw_data"] = []
        return state

    cached = get_cached_result(state["sql_query"])
    data = cached if cached else execute_sql(state["sql_query"])
    if not cached:
        store_cached_result(state["sql_query"], data)
    state["raw_data"] = data
    return state


def role_filter_node(state: GraphState):
    state["filtered_data"] = apply_role_based_filter(
        state["raw_data"], state["role"], state["user_id"]
    )
    return state


def format_node(state):
    # Only include requested columns (excluding internal emp_id)
    requested_columns = [
        c.strip() for c in state["sql_query"]
        .split("FROM")[0].replace("SELECT", "").split(",")
        if c.strip() != "emp_id"
    ]

    final_data = []
    for row in state["filtered_data"]:
        filtered_row = {k: v for k, v in row.items() if k in requested_columns}
        final_data.append(filtered_row)

    # Create user-friendly table as string
    if final_data:
        headers = list(final_data[0].keys())
        rows = [list(r.values()) for r in final_data]

        # Determine column widths
        col_widths = [max(len(str(val)) for val in [hdr] + [row[i] for row in rows]) for i, hdr in enumerate(headers)]

        # Build table
        table_lines = []

        # Header
        header_line = " | ".join(hdr.ljust(col_widths[i]) for i, hdr in enumerate(headers))
        table_lines.append(header_line)
        table_lines.append("-" * len(header_line))

        # Rows
        for row in rows:
            row_line = " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(row))
            table_lines.append(row_line)

        table_str = "\n".join(table_lines)
    else:
        table_str = "No data found for your query."

    state["final_result"] = {
        "query": state["sql_query"],
        "result": table_str
    }

    return state


       

# =========================
# LANGGRAPH DEFINITION
# =========================
graph = StateGraph(GraphState)

graph.add_node("translate", translate_node)
graph.add_node("llm", llm_sql_node)
graph.add_node("explain", explain_sql_node)
graph.add_node("approval", approval_node)
graph.add_node("execute", execution_node)
graph.add_node("filter", role_filter_node)
graph.add_node("format", format_node)

graph.set_entry_point("translate")

graph.add_edge("translate", "llm")
graph.add_edge("llm", "explain")
graph.add_edge("explain", "approval")
graph.add_edge("approval", "execute")
graph.add_edge("execute", "filter")
graph.add_edge("filter", "format")
graph.add_edge("format", END)

app = graph.compile()


# =========================
# PUBLIC FUNCTION
# =========================
def run_text_to_sql(user_input, role, user_id=None):
    state = {
        "user_input": user_input,
        "role": role,
        "user_id": user_id,
        "translated_input": None,
        "sql_query": None,
        "raw_data": None,
        "filtered_data": None,
        "final_result": None,
        "sql_explanation": None,
        "user_approval": None
    }

    result = app.invoke(state)
    return result["final_result"]
