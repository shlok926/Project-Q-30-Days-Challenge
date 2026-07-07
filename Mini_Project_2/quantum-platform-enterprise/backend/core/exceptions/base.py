from fastapi import HTTPException, status

class BaseAPIException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = "GENERIC_ERROR"):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code

class AuthenticationError(BaseAPIException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status.HTTP_401_UNAUTHORIZED, detail, "AUTH_ERROR")

class AuthorizationError(BaseAPIException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(status.HTTP_403_FORBIDDEN, detail, "FORBIDDEN")

class ResourceNotFound(BaseAPIException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status.HTTP_404_NOT_FOUND, detail, "NOT_FOUND")

class ConflictError(BaseAPIException):
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status.HTTP_409_CONFLICT, detail, "CONFLICT")

class BusinessRuleError(BaseAPIException):
    def __init__(self, detail: str = "Business rule violation"):
        super().__init__(status.HTTP_422_UNPROCESSABLE_ENTITY, detail, "BUSINESS_RULE_ERROR")
