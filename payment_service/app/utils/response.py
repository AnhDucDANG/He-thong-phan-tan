from typing import Any, Dict

def success_response(data: Any = None, message: str = "Success") -> Dict:
    return {
        "success": True,
        "message": message,
        "data": data
    }

def error_response(message: str = "Error", details: Any = None) -> Dict:
    return {
        "success": False,
        "message": message,
        "details": details
    }