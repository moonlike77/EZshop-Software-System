from enum import Enum 

class OrderStatus(str, Enum):
    Issued = "ISSUED"
    Paid = "PAID"
    Completed = "COMPLETED"