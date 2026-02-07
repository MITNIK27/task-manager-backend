from enum import Enum

class UserRole(str, Enum):
    USER = "USER"
    QA = "QA"
    ADMIN = "ADMIN"
