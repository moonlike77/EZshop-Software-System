from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DTO.loyality_card_dto import LoyalityCardDTO
from app.controllers.customer_controller import CustomerController
from app.controllers.loyality_card_controller import LoyalityCardController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from fastapi import Response
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.bad_request import BadRequestError
from app.models.user_type import UserType


router = APIRouter(prefix=ROUTES['V1_CUSTOMERS'], tags=["customers"])
controller = CustomerController()
card_controller = LoyalityCardController()

@router.post("/", 
    response_model=CustomerDTO, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
    )
async def create_customer(customer: CustomerDTO):
    """
    Create a new customer.

    - Permissions: Administrator
    - Request body: customerCreateDTO (contains customername, password, type, ...)
    - Returns: Created customer as customerResponseDTO
    - Raises:
      - BadRequestError: when mandatory fields (password, type) are missing or invalid
    - Status code: 201 Created
    """
    if customer.name is None or customer.name == '':
        raise BadRequestError('Name is a mandatory field')
    return await controller.create_customer(customer)
    
@router.get("/", response_model=List[CustomerDTO],
            dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
            )
async def list_customers():
    """
    List all customers.

    - Permissions: Administrator
    - Returns: List of customerResponseDTO
    - Status code: 200 OK
    """
    return await controller.list_customers()


@router.get("/{customer_id}", response_model=CustomerDTO,
            dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
            )
async def get_customer(customer_id: int):
    """
    Retrieve a single customer by ID.

    - Permissions: Administrator
    - Path parameter: customer_id (int)
    - Returns: customerResponseDTO for the requested customer
    - Raises:
      - NotFoundError: when the customer does not exist
    - Status code: 200 OK
    """
    customer = await controller.get_customer(customer_id)
    if not customer:
        raise NotFoundError("customer not found")
    return customer


@router.put("/{customer_id}", response_model=CustomerDTO, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
    )
async def update_customer(customer_id: int, customer: CustomerDTO):
    """
    Update an existing customer.

    - Permissions: Administrator
    - Path parameter: customer_id (int)
    - Request body: customerDTO (fields to update)
    - Returns: Updated customer as customerResponseDTO
    - Raises:
      - NotFoundError: when the customer to update does not exist
    - Status code: 201 Created
    """
    updated = await controller.update_customer(customer_id, customer)
    if not updated:
        raise NotFoundError("customer not found")
    return updated


@router.delete("/{customer_id}", 
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
               )
async def delete_customer(customer_id: int):
    """
    Delete a customer by ID.

    - Permissions: Administrator
    - Path parameter: customer_id (int)
    - Returns: No content (204) on success
    - Raises:
      - NotFoundError: when the customer to delete does not exist
    - Status code: 204 No Content
    """
    success = await controller.delete_customer(customer_id)
    if not success:
        raise NotFoundError("customer not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/cards", 
    response_model=LoyalityCardDTO, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
    )
async def create_loyality_card():
    return await card_controller.create_loyality_card()

@router.patch("/{customer_id}/attach-card/{card_id}",
              response_model=CustomerDTO,
              status_code=status.HTTP_200_OK,
              dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
              )
async def attach_card(customer_id: int, card_id: str):
    return await controller.attach_loyality_card_to_customer(customer_id, card_id)

@router.patch("/cards/{card_id}", response_model=LoyalityCardDTO, status_code=status.HTTP_200_OK,
              dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))])
async def update_points(card_id: int, points: int = Query(...)):
    return await card_controller.update_loyality_card_points(card_id, points)