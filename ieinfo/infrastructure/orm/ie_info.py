from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum as SAEnum, Integer, String, ForeignKey

from config.database.session import Base
from util.security.db_encryption import DBEncryption


class IEType(PyEnum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    TOTAL_INCOME = "TOTAL_INCOME"      # 총 소득 (개별 소득 항목들의 합계)
    TOTAL_EXPENSE = "TOTAL_EXPENSE"    # 총 지출 (개별 지출 항목들의 합계)

class IEInfo(Base):
    __tablename__ = "ie_info"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), ForeignKey("account.session_id"), nullable=False, index=True)
    ie_type = Column(SAEnum(IEType, native_enum=True), nullable=False, index=True)
    
    # 🔒 암호화된 필드 (컬럼 크기 증가: 255 → 1000)
    _key = Column("key", String(1000), nullable=False)
    _value = Column("value", String(1000), nullable=False)
    
    # 평문 필드 (인덱스용)
    year = Column(Integer, nullable=False, index=True)
    month = Column(Integer, nullable=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🔒 암호화 프로퍼티 (인스턴스 전용)
    @property
    def key(self) -> str:
        """항목명 복호화 (예: 급여, 보험료)"""
        if self._key is None or self._key == "":
            return ""
        return DBEncryption.decrypt(self._key)
    
    @key.setter
    def key(self, value: str):
        """항목명 암호화"""
        if value:
            self._key = DBEncryption.encrypt(value)
        else:
            self._key = ""
    
    @property
    def value(self) -> int:
        """금액 복호화"""
        if self._value is None or self._value == "":
            return 0
        return DBEncryption.decrypt_int(self._value)
    
    @value.setter
    def value(self, amount: int):
        """금액 암호화"""
        if amount is not None:
            self._value = DBEncryption.encrypt_int(amount)
        else:
            self._value = ""

    def __repr__(self):
        # ⚠️ 복호화된 값 출력 (로그에 주의)
        return f"<IEInfo id={self.id} session_id={self.session_id} type={self.ie_type.value} key={self.key} value={self.value}>"
