from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.DAO.loyality_card_dao import LoyalityCardDAO
from app.utils import throw_conflict_if_found, find_or_throw_not_found
from app.database.database import AsyncSessionLocal
from typing import Optional


class LoyalityCardRepository:

    def __init__(self, session: Optional[AsyncSession] = None):
        self._session = session

    async def _get_session(self) -> AsyncSession:
        return self._session or AsyncSessionLocal()

    async def create_loyality_card(self) -> LoyalityCardDAO:
        """
        Create loyality card or throw ConflictError if name exists
        """
        async with await self._get_session() as session:
            loyality_card = LoyalityCardDAO(points=0)
            session.add(loyality_card)
            await session.commit()
            await session.refresh(loyality_card)
            return loyality_card

    async def get_loyality_card(self, loyality_card_id: int) -> LoyalityCardDAO | None:
        """
        Get loyality card by id or throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            loyality_card = await session.get(LoyalityCardDAO, loyality_card_id)
            return find_or_throw_not_found(
                [loyality_card] if loyality_card else [],
                lambda _: True,
                f"Loyality card with id '{loyality_card_id}' not found"
            )

#    async def list_loyality_cards(self) -> list[LoyalityCardDAO]:
#        """Get all loyality_cards"""
#        async with await self._get_session() as session:
#            result = await session.execute(select(LoyalityCardDAO))
#            return result.scalars().all()

    async def update_loyality_card_points(self, loyality_card_id: int, updated_points: int) -> LoyalityCardDAO | None:
        """
        Update loyality card information. Throw NotFoundError if not found
        """
        async with await self._get_session() as session:
            db_loyality_card = await session.get(LoyalityCardDAO, loyality_card_id)
            if not db_loyality_card:
                return None

            db_loyality_card.points = updated_points

            await session.commit()
            await session.refresh(db_loyality_card)
            return db_loyality_card

    async def delete_loyality_card(self, loyality_card_id: int) -> bool:
        """
        Delete loyality card by id. Will throw NotFoundError if loyality_card doesn't exist
        """
        async with await self._get_session() as session:
            loyality_card = await session.get(LoyalityCardDAO, loyality_card_id)

            find_or_throw_not_found(
                [loyality_card] if loyality_card else [],
                lambda _: True,
                f"Loyality card with id '{loyality_card_id}' not found"
            )

            await session.delete(loyality_card)
            await session.commit()
            return True