class InventoryAPIError(Exception):
    status_code: int = 500
    error_code: str = "INTERNAL_ERROR"
    message: str = "An unexpected error occurred"

class DatabaseError(InventoryAPIError):
    status_code = 503
    error_code = "DATABASE_ERROR"
