from typing import List, Optional
from app.repositories.customer_repository import CustomerRepository
from app.repositories.loyalty_card_repository import LoyaltyCardRepository
from app.models.DTO.customer_dto import CustomerDTO
from app.services.mapper_service import customerdao_to_dto

class CustomerController:
    def __init__(self):
        self.repo = CustomerRepository()
        self.card_repo = LoyaltyCardRepository()

    async def create_customer(self, Customer_dto: CustomerDTO) -> CustomerDTO: 
        """Create Customer - throws ConflictError if name exists"""
        created = await self.repo.create_customer(Customer_dto.name)
        return customerdao_to_dto(created)

    async def get_customer(self, Customer_id: int) -> Optional[CustomerDTO]:
        """Get Customer by id - throws NotFoundError if not found"""
        dao = await self.repo.get_customer(Customer_id)
        return customerdao_to_dto(dao) if dao else None

    async def list_customers(self) -> List[CustomerDTO]:
        """Get all Customers"""
        daos = await self.repo.list_customers()
        return [customerdao_to_dto(dao) for dao in daos]

    async def update_customer(self, customer_id: int, customer_dto: CustomerDTO) -> Optional[CustomerDTO]:
        """Update Customer - throws NotFoundError if Customer doesn't exist, ConflictError if new name exists"""
        card_before = customerdao_to_dto(await self.repo.get_customer(customer_id)).card
        if customer_dto.card:
            new_card = await self.card_repo.get_loyalty_card(customer_dto.card.card_id)
        else:
            new_card = None
        updated = await self.repo.update_customer(customer_id, customer_dto.name, new_card)
        if card_before is not None and updated.card is None:
            await self.card_repo.delete_loyalty_card(card_before.card_id)

        return customerdao_to_dto(updated) if updated else None
    
    async def attach_loyality_card_to_customer(self, customer_id: int, card_id: str) -> Optional[CustomerDTO]:
        """Attach a loyalty card to a customer - throws NotFoundError if Customer doesn't exist or Loyalty card doesn't exist
           and ConflictError if card already attached to some or same customer"""
        card = await self.card_repo.get_loyalty_card(int(card_id.lstrip('0')))
        attached = await self.repo.update_customer_card(customer_id, card)
        return customerdao_to_dto(attached) if attached else None

    async def delete_customer(self, Customer_id: int) -> bool:
        """Delete Customer - throws NotFoundError if not found"""
        return await self.repo.delete_customer(Customer_id)