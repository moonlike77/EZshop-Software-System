from app.models.DAO.user_dao import UserDAO
from app.models.DTO.user_dto import UserDTO
from app.models.DTO.token_dto import TokenDTO
from app.models.DTO.error_dto import ErrorDTO
from app.models.DAO.customer_dao import CustomerDAO
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DTO.loyality_card_dto import LoyalityCardDTO
from app.models.DAO.loyality_card_dao import LoyalityCardDAO


def create_error_dto(code: int, message: str, name: str) -> ErrorDTO:
    """Create an ErrorDTO instance"""
    return ErrorDTO(code=code, message=message, name=name)

def create_token_dto(token: str) -> TokenDTO:
    return TokenDTO(token=token)

def userdao_to_dto(user_dao: UserDAO) -> UserDTO:
    return UserDTO(
        id=user_dao.id,
        username=user_dao.username,
        password=user_dao.password,
        type=user_dao.type
    )

def userdao_to_responsedto(user_dao: UserDAO) -> UserDTO:
    return UserDTO(
        id=user_dao.id,
        username=user_dao.username,
        type=user_dao.type
    )

def get_customer_details(customer_dao: CustomerDAO) -> CustomerDTO:
    card_dto = None
    if customer_dao.card:
        card_dto = LoyalityCardDTO(
            card_id=str(customer_dao.card.card_id),
            points=customer_dao.card.points
        )
    return CustomerDTO(
        id=customer_dao.id,
        name=customer_dao.name,
        card=card_dto
    )

def carddao_to_carddto(card_dao: LoyalityCardDAO) -> LoyalityCardDTO:
    return LoyalityCardDTO(
        card_id=str(card_dao.card_id),
        points=card_dao.points
    )