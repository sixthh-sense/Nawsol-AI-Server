from dataclasses import dataclass
from datetime import datetime

@dataclass
class CommunityPost:
    provider: str
    board_id: str
    external_post_id: str
    title: str
    author: str
    content: str
    url: str
    view_count: int | None
    recommend_count: int | None
    comment_count: int | None
    posted_at: datetime
    fetched_at: datetime