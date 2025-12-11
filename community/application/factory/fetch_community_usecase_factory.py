from community.adapter.output.paxnet.community_api_adapter import PaxnetCommunityAdapter
from community.application.usecase.fetch_community_usecase import FetchCommunityUsecase
from community.infrastructure.repository.community_repository_impl import CommunityRepositoryImpl

class FetchCommunityUsecaseFactory:
    @staticmethod
    def create():
        adapter = PaxnetCommunityAdapter()
        repo = CommunityRepositoryImpl.get_instance()
        return FetchCommunityUsecase(adapter, repo)