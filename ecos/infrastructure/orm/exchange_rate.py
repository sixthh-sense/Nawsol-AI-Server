from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum as SAEnum, Integer, Float

from config.database.session import Base


class ExchangeType(PyEnum):
    DOLLAR = "0000001"
    YEN = "0000002"
    EURO = "0000003"

class ExchangeRateORM(Base):
    __tablename__ = "exchange_rate"

    id = Column(Integer, primary_key=True, index=True)
    exchange_type = Column(SAEnum(ExchangeType, native_enum=True), nullable=False)
    exchange_rate = Column(Float, nullable=False)
    erm_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ExchangeRateORM id={self.id} exchange_type={self.exchange_type} exchange_rate={self.exchange_rate} erm_date={self.erm_date}>"