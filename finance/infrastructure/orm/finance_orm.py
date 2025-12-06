from sqlalchemy import Column, Integer, ForeignKey, String, Enum as SAEnum
from enum import Enum as PyEnum

from config.database.session import Base

class FinanceType(str, PyEnum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TANGIBLE_ASSETS = "TANGIBLE_ASSETS"
    ETF = "ETF"
    FUND = "FUND"
    BOND = "BOND"

class FinanceORM(Base):
    __tablename__ = "finance"

    id = Column(Integer, primary_key=True)
    user_id = Column(String(255), ForeignKey("account.session_id"), nullable=False)
    type= Column(SAEnum(FinanceType, native_enum=True), nullable=False)
    key = Column(String(255), nullable=False)
    value = Column(String(255), nullable=False)

