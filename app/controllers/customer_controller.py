from typing import List, Optional
from app.repositories.customer_repository import CustomerRepository
from app.models.DTO.customer_dto import CustomerDTO
from app.services.mapper_service import get_customer_details

class CustomerController:
    def __init__(self):
        self.repo = CustomerRepository()

    async def create_customer(self, Customer_dto: CustomerDTO) -> CustomerDTO: 
        """Create Customer - throws ConflictError if Customername exists"""
        created = await self.repo.create_customer(Customer_dto.name)
        return get_customer_details(created)

    async def get_customer(self, Customer_id: int) -> Optional[CustomerDTO]:
        """Get Customer by Customername - throws NotFoundError if not found"""
        dao = await self.repo.get_customer(Customer_id)
        return get_customer_details(dao) if dao else None

    async def list_customers(self) -> List[CustomerDTO]:
        """Get all Customers"""
        daos = await self.repo.list_customers()
        return [get_customer_details(dao) for dao in daos]

    async def update_customer(self, Customer_id: int, Customer_dto: CustomerDTO) -> Optional[CustomerDTO]:
        """Update Customer - throws NotFoundError if Customer doesn't exist, ConflictError if new Customername exists"""
        updated = await self.repo.update_customers(Customer_id, Customer_dto.name)
        return get_customer_details(updated) if updated else None

    async def delete_customer(self, Customer_id: int) -> bool:
        """Delete Customer - throws NotFoundError if not found"""
        return await self.repo.delete_customer(Customer_id)