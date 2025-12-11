from sqlalchemy import (
    Column, Integer, String, DateTime, Text,
    Index
)
from datetime import datetime

from config.database.session import Base


class CommunityPostORM(Base):
    __tablename__ = "community_post"

    id = Column(Integer, primary_key=True)

    provider = Column(String(64), nullable=False)        # "PAXNET_COMMUNITY"
    board_id = Column(String(64), nullable=False)        # N00801, 005930 등
    external_post_id = Column(String(64), nullable=False)  # 953466 등

    title = Column(String(512), nullable=False)
    author = Column(String(128), nullable=True)
    content = Column(Text, nullable=True)
    url = Column(String(2048), nullable=False)

    view_count = Column(Integer, nullable=True)
    recommend_count = Column(Integer, nullable=True)
    comment_count = Column(Integer, nullable=True)

    posted_at = Column(DateTime, nullable=True)
    fetched_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index(
            "uq_community_provider_board_post",
            "provider",
            "board_id",
            "external_post_id",
            unique=True,
        ),
        Index("idx_community_posted_at", "posted_at"),
    )