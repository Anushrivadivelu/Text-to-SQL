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

            # Salary logic
            if col in SENSITIVE_COLUMNS:
                if role == "HR":
                    safe_row[col] = val               # HR sees all salaries
                elif role == "ADMIN":
                    safe_row[col] = mask_value(val)   # Admin masked
                else:
                    # Other roles see only their own salary
                    safe_row[col] = val if emp_id == user_id else mask_value(val)
            else:
                safe_row[col] = val

        filtered.append(safe_row)

    return filtered


