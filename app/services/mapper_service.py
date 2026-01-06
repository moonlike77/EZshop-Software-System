from app.models.DAO.user_dao import UserDAO
from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.DTO.user_dto import UserDTO
from app.models.DTO.order_dto import OrderResponseDTO
from app.models.DTO.product_dto import ProductResponseDTO
from app.models.DTO.token_dto import TokenDTO
from app.models.DTO.error_dto import ErrorDTO


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

def orderdao_to_responsedto(order_dao: OrderDAO, product_barcode: str) -> OrderResponseDTO:
    """Convert OrderDAO to OrderResponseDTO"""
    return OrderResponseDTO(
        id=order_dao.id,
        product_barcode=product_barcode,
        quantity=order_dao.quantity,
        price_per_unit=order_dao.price_per_unit,
        status=order_dao.status.value if hasattr(order_dao.status, 'value') else str(order_dao.status),
        issue_date=order_dao.issue_date
    )

def productdao_to_responsedto(product_dao: ProductDAO) -> ProductResponseDTO:
    """Convert ProductDAO to ProductResponseDTO"""
    return ProductResponseDTO(
        id=product_dao.id,
        description=product_dao.description,
        barcode=product_dao.barcode,
        price_per_unit=product_dao.price_per_unit,
        note=product_dao.note,
        quantity=product_dao.quantity,
        position=product_dao.position
    )