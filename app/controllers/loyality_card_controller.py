from typing import List, Optional
from app.repositories.loyalty_card_repository import LoyaltyCardRepository
from app.models.DTO.loyalty_card_dto import LoyaltyCardDTO
from app.services.mapper_service import carddao_to_carddto

class LoyaltyCardController:
    def __init__(self):
        self.repo = LoyaltyCardRepository()

    async def create_loyalty_card(self) -> LoyaltyCardDTO: 
        """Create loyalty_card - throws ConflictError if loyalty_cardname exists"""
        created = await self.repo.create_loyalty_card()
        return carddao_to_carddto(created)

    async def get_loyalty_card(self, loyalty_card_id: int) -> Optional[LoyaltyCardDTO]:
        """Get loyalty_card by loyalty_cardname - throws NotFoundError if not found"""
        dao = await self.repo.get_loyalty_card(loyalty_card_id)
        return carddao_to_carddto(dao) if dao else None

    async def update_loyalty_card_points(self, loyalty_card_id: int, loyalty_card_points: int) -> Optional[LoyaltyCardDTO]:
        """Update loyalty_card - throws NotFoundError if loyalty_card doesn't exist, ConflictError if new loyalty_cardname exists"""
        updated = await self.repo.update_loyalty_card_points(loyalty_card_id, loyalty_card_points)
        return carddao_to_carddto(updated) if updated else None

    async def delete_loyalty_card(self, loyalty_card_id: int) -> bool:
        """Delete loyalty_card - throws NotFoundError if not found"""
        return await self.repo.delete_loyalty_card(loyalty_card_id)