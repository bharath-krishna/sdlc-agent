from fastapi import HTTPException


class APIError(HTTPException):
    def __init__(self, key, **params):
        if key not in ErrorMessages.ERRORS:
            key = "general_error"

        status_code, reason, template = ErrorMessages.ERRORS[key]
        message = template % params
        super().__init__(status_code=status_code, detail={"reason": reason, "message": message})


class ErrorMessages:
    ERRORS = {
        "general_error": (400, "General error", "%(text)s"),
        "not_found": (404, "Not found", "Resource not found: %(field)s=%(value)s"),
        "duplicated_resource": (400, "Duplicated resource", "Resource already exists: %(value)s"),
        "invalid_field_value": (400, "Invalid field value", "Invalid value for %(field)s: %(value)s"),
        "authorization_error": (403, "Authorization error", "%(text)s"),
        "unauthorized": (401, "Unauthorized", "Authentication required"),
        "invalid_reservation_time": (400, "Invalid reservation time", "Reservation time must be in the future"),
        "reservation_overlap": (400, "Reservation overlap", "This doll is already reserved for the selected time slot"),
    }
