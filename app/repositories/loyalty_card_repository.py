from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models.DAO.loyalty_card_dao import LoyaltyCardDAO
from app.utils import find_or_throw_not_found
from app.models.errors.internal_server_error import InternalServerError
from app.database.database import AsyncSessionLocal
from typing import Optional


class LoyaltyCardRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_loyalty_card(self) -> LoyaltyCardDAO:
        """
        Create loyalty card
        """
        async with await self._get_session() as session:
            loyalty_card = LoyaltyCardDAO(points=0)
            session.add(loyalty_card)
            await session.commit()
            await session.refresh(loyalty_card)
            return loyalty_card

    async def get_loyalty_card(self, loyalty_card_id: int) -> LoyaltyCardDAO | None:
        """
        Get loyalty card by id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            loyalty_card = await session.execute(select(LoyaltyCardDAO)
                                                 .options(joinedload(LoyaltyCardDAO.customer))
                                                 .filter(LoyaltyCardDAO.card_id == loyalty_card_id))
            card_dao = loyalty_card.scalars().first()
            return find_or_throw_not_found(
                [card_dao] if card_dao else [],
                lambda _: True,
                f"loyalty card with id '{loyalty_card_id}' not found"
            )

    async def update_loyalty_card_points(self, loyalty_card_id: int, updated_points: int) -> LoyaltyCardDAO | None:
        """
        Update loyalty card points. Throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            db_loyalty_card = await session.get(LoyaltyCardDAO, loyalty_card_id)
            if not db_loyalty_card:
                return find_or_throw_not_found(
                [],
                lambda _: True,
                f"loyalty card with id '{loyalty_card_id}' not found")
            
            if db_loyalty_card.points < abs(updated_points) and updated_points < 0:
                raise InternalServerError("Not enough points")

            db_loyalty_card.points = db_loyalty_card.points + updated_points

            await session.commit()
            await session.refresh(db_loyalty_card)
            return db_loyalty_card

    async def delete_loyalty_card(self, loyalty_card_id: int) -> bool:
        """
        Delete loyalty card by id. Will throw NotFoundError if loyalty card doesn't exist
        """
        async with await self._get_session() as session:
            loyalty_card = await session.get(LoyaltyCardDAO, loyalty_card_id)

            find_or_throw_not_found(
                [loyalty_card] if loyalty_card else [],
                lambda _: True,
                f"loyalty card with id '{loyalty_card_id}' not found"
            )

            await session.delete(loyalty_card)
            await session.commit()
            return True