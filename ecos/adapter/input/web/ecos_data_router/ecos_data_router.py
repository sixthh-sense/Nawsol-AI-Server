from fastapi import APIRouter

from ecos.application.factory.fetch_ecos_data_usecase_factory import FetchEcosDataUsecaseFactory

ecos_data_router = APIRouter(tags=["ecos"])

@ecos_data_router.get("/exchange_rate")
async def get_exchange_rate():
    usecase = FetchEcosDataUsecaseFactory.create()
    result = await usecase.get_exchange_rate()

    return {
        "source": result.source,
        "fetched_at": result.fetched_at.timestamp.isoformat(),
        "items": [
            {
                "item_type": item.item_type,
                "time": item.time,
                "value": item.value
            } for item in result.items
        ]
    }
