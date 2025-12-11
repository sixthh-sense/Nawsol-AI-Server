from typing import List
from community.adapter.output.paxnet.community_api_adapter import PaxnetCommunityAdapter
from community.application.port.community_repository_port import CommunityRepositoryPort
from community.domain.value_object.community_post import CommunityPost


class FetchCommunityUsecase:
    def __init__(self, adapter: PaxnetCommunityAdapter, repository: CommunityRepositoryPort):
        self.adapter = adapter
        self.repository = repository

    async def fetch_latest(self, board_id: str, page: int = 1, limit: int = 50) -> List[CommunityPost]:
        posts = await self.adapter.fetch_latest(
            board_id=board_id,
            page=page,
            max_posts=limit,
        )
        return posts

    async def fetch_and_save_latest(self, board_id: str, page: int = 1, limit: int = 50) -> List[CommunityPost]:
        posts = await self.adapter.fetch_latest(
            board_id=board_id,
            page=page,
            max_posts=limit,
        )
        if posts:
            self.repository.save_post_batch(posts)
        return posts