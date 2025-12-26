'''SENSITIVE_COLUMNS = {"salary"}
HR_DEPT_ID = 4

def mask_value(_):
    return "****"


def apply_role_based_filter(data, role, user_id=None):
    filtered = []

    for row in data:
        emp_id = row.get("emp_id")
        dept_id = row.get("dept_id")

        if role == "ADMIN":
            allowed = True
        elif role == "HR":
            allowed = dept_id == HR_DEPT_ID
        else:
            allowed = emp_id == user_id

        if not allowed:
            continue

        safe_row = {}
        for col, val in row.items():
            if role != "ADMIN" and col in SENSITIVE_COLUMNS:
                safe_row[col] = mask_value(val)
            else:
                safe_row[col] = val

        filtered.append(safe_row)

    return filtered'''


SENSITIVE_COLUMNS = {"salary"}

def mask_value(_):
    return "****"


def apply_role_based_filter(data, role, user_id=None):
    filtered = []

    for row in data:
        emp_id = row.get("emp_id")

        # ---------------- ROW ACCESS ----------------
        if role in {"ADMIN", "HR"}:
            allowed = True
        else:
            allowed = emp_id == user_id

        if not allowed:
            continue

        # ---------------- COLUMN MASKING ----------------
        safe_row = {}
        for col, val in row.items():
            # Salary visible ONLY to HR
            if col in SENSITIVE_COLUMNS and role != "HR":
                safe_row[col] = mask_value(val)
            else:
                safe_row[col] = val

        filtered.append(safe_row)

    return filtered
