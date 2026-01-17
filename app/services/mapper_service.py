from app.models.DAO.user_dao import UserDAO
from app.models.DAO.order_dao import OrderDAO
from app.models.DAO.product_dao import ProductDAO
from app.models.DTO.user_dto import UserDTO
from app.models.DTO.order_dto import OrderResponseDTO
from app.models.DTO.product_dto import ProductResponseDTO
from app.models.DTO.token_dto import TokenDTO
from app.models.DTO.error_dto import ErrorDTO
from app.models.DAO.sale_dao import SaleDAO
from app.models.DAO.sale_line_dao import SaleLineDAO
from app.models.DTO.sale_dto import SaleDTO
from app.models.DTO.sale_line_dto import SaleLineDTO
from app.models.DAO.customer_dao import CustomerDAO
from app.models.DTO.customer_dto import CustomerDTO
from app.models.DTO.loyalty_card_dto import LoyaltyCardDTO
from app.models.DAO.loyalty_card_dao import LoyaltyCardDAO
from sqlalchemy import inspect


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


def saledao_to_dto(sale_dao: SaleDAO) -> SaleDTO:
    state = inspect(sale_dao)

    if "lines" in state.unloaded:
        lines_dao = []
    else:
        lines_dao = sale_dao.lines or []

    return SaleDTO(
        id=sale_dao.id,
        status=sale_dao.status,
        discount_rate=sale_dao.discount_rate,
        created_at=sale_dao.created_at,
        closed_at=sale_dao.closed_at,
        lines=[salelinedao_to_dto(line) for line in lines_dao],
    )

def customerdao_to_dto(customer_dao: CustomerDAO) -> CustomerDTO:
    card_dto = None
    if customer_dao.card:
        card_dto = carddao_to_carddto(customer_dao.card)
    return CustomerDTO(
        id=customer_dao.id,
        name=customer_dao.name,
        card=card_dto
    )

def carddao_to_carddto(card_dao: LoyaltyCardDAO) -> LoyaltyCardDTO:
    card_id_int = card_dao.card_id
    card_id_str = str(card_id_int).zfill(10)
    return LoyaltyCardDTO(
        card_id=card_id_str,
        points=card_dao.points
    )

def orderdao_to_responsedto(order_dao: OrderDAO, product_barcode: str) -> OrderResponseDTO:
    """Convert OrderDAO to OrderResponseDTO"""
    status_val = order_dao.status.value if hasattr(order_dao.status, 'value') else str(order_dao.status)
    return OrderResponseDTO(
        id=order_dao.id,
        product_barcode=product_barcode,
        quantity=order_dao.quantity,
        price_per_unit=order_dao.price_per_unit,
        status=str(status_val).upper(),
        issue_date=order_dao.issue_date,
        is_reorder_warning=order_dao.is_reorder_warning
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