from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.DAO.customer_dao import CustomerDAO
from app.utils import throw_conflict_if_found, find_or_throw_not_found
from app.database.database import AsyncSessionLocal
from typing import Optional


class CustomerRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_customer(self, name: str, surname: str) -> CustomerDAO:
        """
        Create customer or throw ConflictError if name exists
        """
        async with await self._get_session() as session:
            result = await session.execute(select(CustomerDAO).filter(CustomerDAO.name == name))
            existing_customers = result.scalars().all()

            throw_conflict_if_found(
                existing_customers,
                lambda _: True,
                f"Customer with name '{name}' already exists"
            )

            customer = CustomerDAO(name=name, surname=surname)
            session.add(customer)
            await session.commit()
            await session.refresh(customer)
            return customer

    async def get_customer(self, customer_id: int) -> CustomerDAO | None:
        """
        Get customer by id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            customer = await session.get(CustomerDAO, customer_id)
            return find_or_throw_not_found(
                [customer] if customer else [],
                lambda _: True,
                f"Customer with id '{customer_id}' not found"
            )

    async def get_customer_by_name(self, name: str) -> CustomerDAO | None:
        """
        Get customer by name or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            result = await session.execute(select(CustomerDAO).filter(CustomerDAO.name == name))
            customers = result.scalars().all()
            return find_or_throw_not_found(
                customers,
                lambda _: True,
                f"Customer with name '{name}' not found"
            )

    async def list_customers(self) -> list[CustomerDAO]:
        """Get all customers"""
        async with await self._get_session() as session:
            result = await session.execute(select(CustomerDAO))
            return result.scalars().all()

    async def update_customers(self, customer_id: int, updated_name: str, updated_surname: str) -> CustomerDAO | None:
        """
        Update customer information. Throw NotFoundError if not found or ConflictError if the new name exists
        """
        async with await self._get_session() as session:
            db_customer = await session.get(CustomerDAO, customer_id)
            if not db_customer:
                return None

            result_conflict = await session.execute(select(CustomerDAO).filter(CustomerDAO.name == updated_name))
            conflicting_name = result_conflict.scalars().all()
            throw_conflict_if_found(
                conflicting_name,
                lambda _: True,
                f"Customer with name '{updated_name}' already exists"
            )

            db_customer.name = updated_name
            db_customer.surname = updated_surname

            await session.commit()
            await session.refresh(db_customer)
            return db_customer

    async def delete_customer(self, customer_id: int) -> bool:
        """
        Delete customer by id. Will throw NotFoundError if customer doesn't exist
        """
        async with await self._get_session() as session:
            customer = await session.get(CustomerDAO, customer_id)

            find_or_throw_not_found(
                [customer] if customer else [],
                lambda _: True,
                f"Customer with id '{customer_id}' not found"
            )

            await session.delete(customer)
            await session.commit()
            return True