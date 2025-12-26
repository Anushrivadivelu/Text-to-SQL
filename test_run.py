from backend.text_to_sql_langgraph_flow import run_text_to_sql

m=input("enter the query ")

response = run_text_to_sql(
    user_input=m,
    role="ADMIN",
    user_id=101
)

print(response)

