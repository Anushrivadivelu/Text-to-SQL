def format_table(data):
    if not data:
        return {"columns": [], "rows": []}

    columns = list(data[0].keys())
    rows = [[row[col] for col in columns] for row in data]

    return {
        "columns": columns,
        "rows": rows
    }
