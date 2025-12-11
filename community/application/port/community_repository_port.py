from abc import ABC, abstractmethod
from typing import List

from community.domain.value_object.community_post import CommunityPost


class CommunityRepositoryPort(ABC):

    @abstractmethod
    def save_post_batch(self, posts: List[CommunityPost]) -> List[CommunityPost]:
        """
        provider + board_id + external_post_id 기준으로
        이미 있는 건 건너뛰고, 새로운 글만 insert.
        """
        ...
