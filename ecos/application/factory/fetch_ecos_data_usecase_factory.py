from ecos.adapter.output.ecos.ecos_data_api_adapter import EcosDataApiAdapter
from ecos.application.usecase.ecos_usecase import FetchEcosUseCase


class FetchEcosDataUsecaseFactory:
    @staticmethod
    def create() -> FetchEcosUseCase:
        api_adapter = EcosDataApiAdapter()
        return FetchEcosUseCase(api_adapter)