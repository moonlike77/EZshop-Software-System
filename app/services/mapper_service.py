from app.models.DAO.user_dao import UserDAO
from app.models.DTO.user_dto import UserDTO
from app.models.DTO.token_dto import TokenDTO
from app.models.DTO.error_dto import ErrorDTO
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.DTO.sale_dto import SaleDTO, SaleLineDTO


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

def salelinedao_to_dto(line_dao: SaleLineDAO) -> SaleLineDTO:  # added sale_line
    return SaleLineDTO(
        id=line_dao.id,
        sale_id=line_dao.sale_id,
        product_barcode=line_dao.product_barcode,
        quantity=line_dao.quantity,
        price_per_unit=line_dao.price_per_unit,
        discount_rate=line_dao.discount_rate,
    )


def saledao_to_dto(sale_dao: SaleDAO) -> SaleDTO:  # added sale
    return SaleDTO(
        id=sale_dao.id,
        status=sale_dao.status,
        discount_rate=sale_dao.discount_rate,
        created_at=sale_dao.created_at,
        closed_at=sale_dao.closed_at,
        lines=[],
    )