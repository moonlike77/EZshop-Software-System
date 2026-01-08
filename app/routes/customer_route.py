from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DTO.loyalty_card_dto import LoyaltyCardDTO
from app.controllers.customer_controller import CustomerController
from app.controllers.loyalty_card_controller import LoyaltyCardController
from app.middleware.auth_middleware import authenticate_user
from app.config.config import ROUTES
from fastapi import Response
from app.models.errors.notfound_error import NotFoundError
from app.models.errors.conflict_error import ConflictError
from app.models.errors.bad_request import BadRequestError
from app.models.user_type import UserType


router = APIRouter(prefix=ROUTES['V1_CUSTOMERS'], tags=["customers"])
controller = CustomerController()
card_controller = LoyaltyCardController()

@router.post("/", 
    response_model=CustomerDTO, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
    )
async def create_customer(customer: CustomerDTO):
    """
    Create a new customer.

    - Permissions: Administrator, Cashier, ShopManager
    - Request body: CustomerDTO (contains name and card will be initially null)
    - Returns: Created customer as CustomerDTO
    - Raises:
      - BadRequestError: when mandatory field (name) is missing or invalid
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

    - Permissions: Administrator, Cashier, ShopManager
    - Returns: List of CustomerDTO
    - Status code: 200 OK
    """
    return await controller.list_customers()


@router.get("/{customer_id}", response_model=CustomerDTO,
            dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
            )
async def get_customer(customer_id: int):
    """
    Retrieve a single customer by ID.

    - Permissions: Administrator, Cashier, ShopManager
    - Path parameter: customer_id (int)
    - Returns: CustomerDTO for the requested customer
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

    - Permissions: Administrator, Cashier, ShopManager
    - Path parameter: customer_id (int)
    - Request body: CustomerDTO (fields to update)
    - Returns: Updated customer as CustomerDTO
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

    - Permissions: Administrator, Cashier, ShopManager
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
    response_model=LoyaltyCardDTO, 
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
    )
async def create_loyality_card():
    """
    Create a loyalty card.

    - Permissions: Administrator, Cashier, ShopManager
    - Body: no body because cards are created with sequential ids and points start from 0
    - Status code: 201 Created
    """
    return await card_controller.create_loyalty_card()

@router.patch("/{customer_id}/attach-card/{card_id}",
              response_model=CustomerDTO,
              status_code=status.HTTP_200_OK,
              dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))]
              )
async def attach_card(customer_id: int, card_id: str):
    """
    Attach a loyalty card to a customer.

    - Permissions: Administrator, Cashier, ShopManager
    - Path parameter: customer_id (int), card_id (int)
    - Returns: CustomerDTO of the customer with card attached
    - Raises:
      - NotFoundError: when the customer does not exist or when the card does not exist
      - ConflictError: when the card is associated to the same customer or some other customer
    - Status code: 200 OK
    """
    attached =  await controller.attach_loyalty_card_to_customer(customer_id, card_id)
    if not attached:
        raise ConflictError("Card already attached")
    return attached

@router.patch("/cards/{card_id}", response_model=LoyaltyCardDTO, status_code=status.HTTP_200_OK,
              dependencies=[Depends(authenticate_user([UserType.Administrator, UserType.Cashier, UserType.ShopManager]))])
async def update_points(card_id: int, points: int = Query(...)):
    """
    Update points on a loyalty card.

    - Permissions: Administrator, Cashier, ShopManager
    - Path parameter: card_id (int)
    - Returns: LoyaltyCardDTO
    - Raises:
      - NotFoundError: when the card does not exist
    - Status code: 200 OK
    """
    return await card_controller.update_loyalty_card_points(card_id, points)