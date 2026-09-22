"""
Presenova Standard API Response Utilities (BUG-10)
Enforces a consistent contract across all backend endpoints:
Success: {"success": True, "message": "...", ...data}
Error:   {"success": False, "error": "ErrorCode", "message": "..."}
"""

from typing import Any, Dict, Optional
from flask import jsonify, Response


def ok(
    data: Optional[Dict[str, Any]] = None,
    message: Optional[str] = None,
    status: int = 200,
    **kwargs: Any
) -> tuple[Response, int]:
    """
    Construct a standardized success JSON response.
    """
    payload: Dict[str, Any] = {
        "success": True,
        "status": "success",
    }
    if message:
        payload["message"] = message
    if data:
        payload.update(data)
    if kwargs:
        payload.update(kwargs)

    return jsonify(payload), status


def err(
    error_code: str,
    message: str,
    status: int = 400,
    details: Optional[Any] = None,
    **kwargs: Any
) -> tuple[Response, int]:
    """
    Construct a standardized error JSON response.
    """
    payload: Dict[str, Any] = {
        "success": False,
        "status": "error",
        "error": error_code,
        "message": message,
    }
    if details is not None:
        payload["details"] = details
    if kwargs:
        payload.update(kwargs)

    return jsonify(payload), status
