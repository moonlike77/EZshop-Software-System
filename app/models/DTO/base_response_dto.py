from pydantic import BaseModel

class SuccessResponseDTO(BaseModel):
    success: bool = True
