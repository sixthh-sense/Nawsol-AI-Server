from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Float

from config.database.session import Base


class InterestRateORM(Base):
    __tablename__ = "interest_rate"

    id = Column(Integer, primary_key=True, index=True)
    interest_type = Column(String(255), nullable=False)
    interest_rate = Column(Float, nullable=False)
    erm_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InterestRateORM id={self.id} interest_type={self.interest_type} interest_rate={self.interest_rate} erm_date={self.erm_date}>"