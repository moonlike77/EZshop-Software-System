from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from datetime import datetime

from app.config.config import ROUTES
from app.controllers.accounting_controller import AccountingController
from app.models.DTO.transaction_dto import TransactionCreateDTO, TransactionResponseDTO, BalanceResponseDTO
from app.models.user_type import UserType
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.user_dto import UserDTO

router = APIRouter(prefix=ROUTES['V1_GENERAL'], tags=["Accounting"])
controller = AccountingController()

# Allowed roles: Administrator only for sensitive balance operations
ADMIN_ONLY = [UserType.Administrator]


@router.get("/balance", 
    response_model=BalanceResponseDTO)
async def get_balance(
    current_user: UserDTO = Depends(authenticate_user(ADMIN_ONLY))
):
    """
    Get current system balance.
    """
    balance = await controller.get_current_balance()
    return BalanceResponseDTO(balance=balance)

from app.models.DTO.base_response_dto import SuccessResponseDTO

@router.post("/balance/set", 
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseDTO)
async def set_balance(
    amount: float = Query(..., description="The amount to set the balance to"),
    current_user: UserDTO = Depends(authenticate_user(ADMIN_ONLY))
):
    """
    Set system balance to a specific amount.
    Creates a correction transaction.
    """
    try:
        await controller.set_balance(amount, current_user.id)
        return SuccessResponseDTO(success=True)
    except ValueError as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=421, detail=str(e))

@router.post("/balance/reset", 
    status_code=status.HTTP_205_RESET_CONTENT)
async def reset_balance(
    current_user: UserDTO = Depends(authenticate_user(ADMIN_ONLY))
):
    """
    Reset system balance to 0.
    Creates a correction transaction.
    """
    await controller.reset_balance(current_user.id)
    return None
