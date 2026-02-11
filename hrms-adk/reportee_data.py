from google.adk.tools import FunctionTool

def get_reportee_details(employee_id: str) -> dict:
    """
    Returns reportee details for an employee.
    """
    return {
        "employee_id": employee_id,
        "reportees": [
            {"name": "John", "leave_balance": 5},
            {"name": "Priya", "leave_balance": 8}
        ]
    }

# ✅ CORRECT for your ADK version
reportee_tool = FunctionTool(get_reportee_details)
