from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, DateTime, Enum as SAEnum, Integer

from config.database.session import Base
from util.security.db_encryption import DBEncryption


class OAuthProvider(PyEnum):
    GOOGLE = "GOOGLE"
    NAVER = "NAVER"
    KAKAO = "KAKAO"

class YN(PyEnum):
    Y = "Y"
    N = "N"

class AccountORM(Base):
    __tablename__ = "account"

    session_id = Column(String(255), primary_key=True, nullable=False)
    oauth_id = Column(String(255), nullable=False)
    oauth_type = Column(SAEnum(OAuthProvider, native_enum=True), nullable=False, index=True)

    # 🔒 암호화된 필드 (컬럼 크기 증가: 255 → 1000)
    # Fernet 암호화는 원본보다 약 1.5배 크기 증가
    _nickname = Column("nickname", String(1000), nullable=True)
    _name = Column("name", String(1000), nullable=True)
    _email = Column("email", String(1000), nullable=True)
    _phone_number = Column("phone_number", String(1000), nullable=True)
    
    # 평문 필드
    profile_image = Column(String(255), nullable=True)
    active_status = Column(SAEnum(YN, native_enum=True), nullable=False, default=YN.Y)
    role_id = Column(String(255), nullable=True)

    automatic_analysis_cycle = Column(Integer, nullable=True, default=0)
    target_period = Column(Integer, nullable=True, default=0)
    target_amount = Column(Integer, nullable=True, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 🔒 암호화 프로퍼티 (인스턴스 전용)
    @property
    def nickname(self) -> str:
        """닉네임 복호화"""
        if self._nickname is None or self._nickname == "":
            return ""
        return DBEncryption.decrypt(self._nickname)
    
    @nickname.setter
    def nickname(self, value: str):
        """닉네임 암호화"""
        if value:
            self._nickname = DBEncryption.encrypt(value)
        else:
            self._nickname = ""
    
    @property
    def name(self) -> str:
        """이름 복호화"""
        if self._name is None or self._name == "":
            return ""
        return DBEncryption.decrypt(self._name)
    
    @name.setter
    def name(self, value: str):
        """이름 암호화"""
        if value:
            self._name = DBEncryption.encrypt(value)
        else:
            self._name = ""
    
    @property
    def email(self) -> str:
        """이메일 복호화"""
        if self._email is None or self._email == "":
            return ""
        return DBEncryption.decrypt(self._email)
    
    @email.setter
    def email(self, value: str):
        """이메일 암호화"""
        if value:
            self._email = DBEncryption.encrypt(value)
        else:
            self._email = ""
    
    @property
    def phone_number(self) -> str:
        """전화번호 복호화"""
        if self._phone_number is None or self._phone_number == "":
            return ""
        return DBEncryption.decrypt(self._phone_number)
    
    @phone_number.setter
    def phone_number(self, value: str):
        """전화번호 암호화"""
        if value:
            self._phone_number = DBEncryption.encrypt(value)
        else:
            self._phone_number = ""

    def __repr__(self):
        # ⚠️ 복호화된 값 출력 (로그에 주의)
        return f"<AccountORM id={self.session_id} email={self.email} oauth_type={self.oauth_type} nickname={self.nickname}>"
