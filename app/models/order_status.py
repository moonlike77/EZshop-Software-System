from enum import Enum 

class OrderStatus(str, Enum):
    Issued = "Issued"
    Paid = "Paid"
    Completed = "Completed"