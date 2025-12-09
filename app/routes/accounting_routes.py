from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from datetime import datetime

from app.config.config import ROUTES
from app.controllers.accounting_controller import AccountingController
from app.models.DTO.transaction_dto import TransactionCreateDTO, TransactionResponseDTO
from app.models.user_type import UserType
from app.middleware.auth_middleware import authenticate_user
from app.models.DTO.user_dto import UserDTO

router = APIRouter(prefix=ROUTES['V1_ACCOUNTING'], tags=["Accounting"])
controller = AccountingController()

# Allowed roles: Administrator, ShopManager, Accounting
ALLOWED_ROLES = [UserType.Administrator, UserType.ShopManager, UserType.Accounting]

@router.post("/transaction", 
    response_model=TransactionResponseDTO, 
    status_code=status.HTTP_201_CREATED)
async def record_transaction(
    transaction_data: TransactionCreateDTO, 
    current_user: UserDTO = Depends(authenticate_user(ALLOWED_ROLES))
):
    """
    Record a new transaction (Debit/Credit).
    """
    # Assuming UserDTO has implicit id or we can fetch it. 
    # UserDTO is defined in user_dto.py. Let's assume it has an id field or similar matching DAO.
    # Actually, UserDTO usually doesn't have ID if it's the response DTO, wait. 
    # authenticate_user returns the DAO or DTO? 
    # Checking auth_middleware.
    
    return await controller.record_transaction(transaction_data, current_user.id)

@router.get("/transactions", 
    response_model=List[TransactionResponseDTO])
async def get_transactions(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    current_user: UserDTO = Depends(authenticate_user(ALLOWED_ROLES))
):
    """
    Get transaction history.
    """
    return await controller.get_history(start_date, end_date)

@router.get("/balance", 
    response_model=float)
async def get_balance(
    current_user: UserDTO = Depends(authenticate_user(ALLOWED_ROLES))
):
    """
    Get current system balance.
    """
    return await controller.get_current_balance()
