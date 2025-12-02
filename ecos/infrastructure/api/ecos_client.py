import os
from datetime import datetime, timedelta

import aiohttp

from ecos.infrastructure.orm.exchange_rate import ExchangeType


class EcosClient:
    ECOS_BASE_URL = os.getenv("ECOS_BASE_URL")
    ECOS_EXCHANGE_RATE_URL = os.getenv("ECOS_EXCHANGE_RATE_URL")
    ECOS_INTEREST_RATE_URL = os.getenv("ECOS_INTEREST_RATE_URL")
    ECOS_API_KEY = os.getenv("ECOS_API_KEY")
    ECOS_EXCHANGE_SERVICE_KEY = os.getenv("ECOS_EXCHANGE_SERVICE_KEY")
    ECOS_INTEREST_SERVICE_KEY = os.getenv("ECOS_INTEREST_SERVICE_KEY")

    async def get_exchange_rate(self) -> list[dict]:
        today = datetime.today().strftime("%Y%m%d")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
        base_url = f"{self.ECOS_BASE_URL}/{self.ECOS_EXCHANGE_RATE_URL}/{self.ECOS_API_KEY}/json/kr/1/100/{self.ECOS_EXCHANGE_SERVICE_KEY}/D/{yesterday}/{today}"

        results = []
        
        async with (aiohttp.ClientSession() as session):
            async with session.get(f"{base_url}/{ExchangeType.DOLLAR.value}") as response:
                if response.status != 200:
                    raise Exception(f"Ecos API Dollar Error {response.status}")
                data = await response.json()

                if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
                    results.extend(data['StatisticSearch']['row'])

            async with session.get(f"{base_url}/{ExchangeType.YEN.value}") as response:
                if response.status != 200:
                    raise Exception(f"Ecos API Yen Error {response.status}")
                data = await response.json()

                if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
                    results.extend(data['StatisticSearch']['row'])
                    
            async with session.get(f"{base_url}/{ExchangeType.EURO.value}") as response:
                if response.status != 200:
                    raise Exception(f"Ecos API Euro Error {response.status}")
                data = await response.json()

                if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
                    results.extend(data['StatisticSearch']['row'])

        return results

    async def get_interest_rate(self) -> list[dict]:
        today = datetime.today().strftime("%Y%m%d")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
        base_url = f"{self.ECOS_BASE_URL}/{self.ECOS_INTEREST_RATE_URL}/{self.ECOS_API_KEY}/json/kr/1/100/{self.ECOS_INTEREST_SERVICE_KEY}/D/{yesterday}/{today}"

        results = []

        async with (aiohttp.ClientSession() as session):
            async with session.get(f"{base_url}") as response:
                if response.status != 200:
                    raise Exception(f"Ecos API Interest Error {response.status}")
                data = await response.json()

                if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
                    results.extend(data['StatisticSearch']['row'])

        return results