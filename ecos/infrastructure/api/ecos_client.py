import os
import aiohttp

from datetime import datetime, timedelta

class EcosClient:
    ECOS_BASE_URL = os.getenv("ECOS_BASE_URL")
    ECOS_EXCHANGE_RATE_URL = os.getenv("ECOS_EXCHANGE_RATE_URL")
    ECOS_INTEREST_RATE_URL = os.getenv("ECOS_INTEREST_RATE_URL")
    ECOS_API_KEY = os.getenv("ECOS_API_KEY")

    async def get_exchange_rate(self) -> list[dict]:
        today = datetime.today().strftime("%Y%m%d")
        yesterday = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
        base_url = f"{self.ECOS_BASE_URL}/{self.ECOS_EXCHANGE_RATE_URL}/{self.ECOS_API_KEY}/json/kr/1/100/731Y001/D/{yesterday}/{today}"
        dollar = "0000001"
        yen = "0000002"
        euro = "0000003"
        
        results = []
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{base_url}/{dollar}") as response:
                if response.status != 200:
                    raise Exception(f"Ecos API Dollar Error {response.status}")
                data = await response.json()

                if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
                    results.extend(data['StatisticSearch']['row'])

            async with session.get(f"{base_url}/{yen}") as response:
                if response.status != 200:
                    raise Exception(f"Ecos API Yen Error {response.status}")
                data = await response.json()

                if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
                    results.extend(data['StatisticSearch']['row'])
                    
            async with session.get(f"{base_url}/{euro}") as response:
                if response.status != 200:
                    raise Exception(f"Ecos API Euro Error {response.status}")
                data = await response.json()

                if 'StatisticSearch' in data and 'row' in data['StatisticSearch']:
                    results.extend(data['StatisticSearch']['row'])

        print(results)
        return results