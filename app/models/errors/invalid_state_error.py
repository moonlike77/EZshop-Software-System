from app.models.errors.app_error import AppError

class InvalidStateError(AppError):
    
    def __init__(self, message: str):
        super().__init__(message, 420)
        self.name = "InvalidStateError"

