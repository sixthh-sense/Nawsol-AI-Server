"""
ANALYZE_HISTORY ORM 모델
미래 자산 예측 GPT 조언 학습 저장
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DECIMAL, DateTime, Index
from sqlalchemy.sql import func

from config.database.session import Base


class AnalyzeHistory(Base):
    """
    미래 자산 예측 분석 이력 테이블
    GPT가 생성한 조언을 학습하여 유사한 패턴의 사용자에게 재사용
    """
    __tablename__ = "ANALYZE_HISTORY"
    
    # Primary Key
    analyze_id = Column("ANALYZE_ID", Integer, primary_key=True, autoincrement=True)
    
    # 소비 패턴 & 자산 수준
    monthly_income = Column("MONTHLY_INCOME", Integer, nullable=False, index=True)
    monthly_expense = Column("MONTHLY_EXPENSE", Integer, nullable=False, index=True)
    monthly_surplus = Column("MONTHLY_SURPLUS", Integer, nullable=False)
    expense_ratio = Column("EXPENSE_RATIO", DECIMAL(5, 2), nullable=False, index=True)
    savings_ratio = Column("SAVINGS_RATIO", DECIMAL(5, 2), nullable=False)
    
    # 지출 카테고리 비율
    essential_ratio = Column("ESSENTIAL_RATIO", DECIMAL(5, 2), default=0)
    leisure_ratio = Column("LEISURE_RATIO", DECIMAL(5, 2), default=0)
    investment_ratio = Column("INVESTMENT_RATIO", DECIMAL(5, 2), default=0)
    other_ratio = Column("OTHER_RATIO", DECIMAL(5, 2), default=0)
    
    # 자산 수준
    asset_level = Column("ASSET_LEVEL", String(20), nullable=False, index=True)
    
    # GPT 조언
    gpt_advice = Column("GPT_ADVICE", Text, nullable=False)
    
    # 메타 정보
    use_count = Column("USE_COUNT", Integer, default=1)
    created_at = Column("CREATED_AT", DateTime, default=func.now(), nullable=False)
    last_used_at = Column("LAST_USED_AT", DateTime, default=func.now(), onupdate=func.now())
    
    # 복합 인덱스: 패턴 검색 최적화
    __table_args__ = (
        Index('idx_pattern', 'MONTHLY_INCOME', 'MONTHLY_EXPENSE', 'EXPENSE_RATIO'),
        Index('idx_asset_level', 'ASSET_LEVEL'),
        Index('idx_created_at', 'CREATED_AT'),
    )
    
    def __repr__(self):
        return f"<AnalyzeHistory(id={self.analyze_id}, income={self.monthly_income}, expense={self.monthly_expense}, level={self.asset_level})>"
