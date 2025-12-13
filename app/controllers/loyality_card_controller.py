from typing import List, Optional
from app.repositories.loyality_card_repository import LoyalityCardRepository
from app.models.DTO.loyality_card_dto import LoyalityCardDTO
from app.services.mapper_service import carddao_to_carddto

class LoyalityCardController:
    def __init__(self):
        self.repo = LoyalityCardRepository()

    async def create_loyality_card(self) -> LoyalityCardDTO: 
        """Create loyality_card - throws ConflictError if loyality_cardname exists"""
        created = await self.repo.create_loyality_card()
        return carddao_to_carddto(created)

    async def get_loyality_card(self, loyality_card_id: int) -> Optional[LoyalityCardDTO]:
        """Get loyality_card by loyality_cardname - throws NotFoundError if not found"""
        dao = await self.repo.get_loyality_card(loyality_card_id)
        return carddao_to_carddto(dao) if dao else None

    async def update_loyality_card_points(self, loyality_card_id: int, loyality_card_points: int) -> Optional[LoyalityCardDTO]:
        """Update loyality_card - throws NotFoundError if loyality_card doesn't exist, ConflictError if new loyality_cardname exists"""
        updated = await self.repo.update_loyality_card_points(loyality_card_id, loyality_card_points)
        return carddao_to_carddto(updated) if updated else None

    async def delete_loyality_card(self, loyality_card_id: int) -> bool:
        """Delete loyality_card - throws NotFoundError if not found"""
        return await self.repo.delete_loyality_card(loyality_card_id)