from ecos.adapter.output.ecos.ecos_data_api_adapter import EcosDataApiAdapter
from ecos.domain.ecos_data import EcosData


class FetchEcosUseCase:
    def __init__(self, adapter: EcosDataApiAdapter):
        self.adapter = adapter

    async def get_exchange_rate(self) -> EcosData:
        return await self.adapter.get_exchange_rate()