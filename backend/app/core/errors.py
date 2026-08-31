"""Domain-level exceptions, translated into HTTP responses by the central
exception handlers registered in main.py — services and repositories raise
these without knowing anything about HTTP status codes.
"""


class NotFoundError(Exception):
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(message)


class ConflictError(Exception):
    def __init__(self, message: str = "Conflict with existing resource"):
        self.message = message
        super().__init__(message)


class ValidationError(Exception):
    def __init__(self, message: str = "Invalid request"):
        self.message = message
        super().__init__(message)
