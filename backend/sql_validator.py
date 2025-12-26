def validate_user_input(user_input):
    if not user_input.strip():
        raise ValueError("Empty input")
    return user_input.strip()


def validate_sql(sql_query):
    lines = sql_query.strip().splitlines()

    sql = ""
    for line in lines:
        if line.upper().startswith("SELECT"):
            sql = line
            break

    if not sql:
        raise ValueError("No SELECT found")

    forbidden = ["DROP", "DELETE", "UPDATE", "INSERT"]
    if any(f in sql.upper() for f in forbidden):
        raise ValueError("Unsafe SQL")

    return sql
