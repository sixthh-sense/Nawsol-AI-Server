from datetime import datetime
from typing import List

from ecos.domain.ecos_data import EcosData
from ecos.domain.ecos_item import EcosItem
from ecos.domain.value_object.ecos_source import EcosSource
from ecos.infrastructure.api.ecos_client import EcosClient


class EcosDataApiAdapter:
    def __init__(self):
        self.client = EcosClient()

    async def get_exchange_rate(self) -> EcosData:
        raw_items = await self.client.get_exchange_rate()
        from ecos.domain.value_object.timestamp import Timestamp
        items: List[EcosItem] = [
            EcosItem(
                item_type=item.get("ITEM_NAME1"),
                time=item.get("TIME"),
                value=item.get("DATA_VALUE")
            )
            for item in raw_items
        ]
        return EcosData(
            items=items,
            source=EcosSource("ECOS_EXCHANGE_RATE"),
            fetched_at=Timestamp(datetime.now())
        )

    async def get_interest_rate(self) -> EcosData:
        raw_items = await self.client.get_interest_rate()
        from ecos.domain.value_object.timestamp import Timestamp
        items: List[EcosItem] = [
            EcosItem(
                item_type=item.get("ITEM_NAME1"),
                time=item.get("TIME"),
                value=item.get("DATA_VALUE")
            )
            for item in raw_items
        ]
        return EcosData(
            items=items,
            source=EcosSource("ECOS_EXCHANGE_RATE"),
            fetched_at=Timestamp(datetime.now())
        )
