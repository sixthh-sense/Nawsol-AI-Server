from datetime import datetime
from typing import List

from ecos.adapter.output.ecos.ecos_data_api_adapter import EcosDataApiAdapter
from ecos.application.port.ecos_repository_port import EcosRepositoryPort
from ecos.domain.ecos import Ecos
from ecos.domain.ecos_data import EcosData
from ecos.domain.ecos_interest import EcosInterest
from ecos.infrastructure.orm.exchange_rate import ExchangeType
from util.log.log import Log

logger = Log.get_logger()
class FetchEcosUseCase:
    def __init__(self, adapter: EcosDataApiAdapter, repository: EcosRepositoryPort):
        self.adapter = adapter
        self.repository = repository

    async def get_exchange_rate(self) -> EcosData:
        return await self.adapter.get_exchange_rate()

    async def fetch_and_save_exchange_rate(self) -> List[Ecos]:
        """
        ECOS API에서 환율 데이터를 조회하고 데이터베이스에 저장한다.
        
        Returns:
            저장된 Ecos 도메인 엔티티 리스트
        """
        # 1. API에서 raw 데이터 조회
        from ecos.infrastructure.api.ecos_client import EcosClient
        client = EcosClient()
        raw_items = await client.get_exchange_rate()
        
        # 2. Raw 데이터를 Domain Entity로 변환
        ecos_entities = []
        for item in raw_items:
            # ITEM_CODE1을 ExchangeType으로 변환
            item_code = item.get('ITEM_CODE1')
            try:
                exchange_type = ExchangeType(item_code)
            except ValueError:
                # 알 수 없는 통화 코드는 스킵
                logger.warning(f"Unknown exchange type: {item_code}")
                continue
            
            # TIME을 datetime으로 변환
            time_str = item.get('TIME')
            try:
                erm_date = datetime.strptime(time_str, '%Y%m%d')
            except (ValueError, TypeError):
                logger.warning(f"Invalid time format: {time_str}")
                continue

            data_value = item.get('DATA_VALUE')
            try:
                exchange_rate = float(data_value)
            except (ValueError, TypeError):
                logger.warning(f"Invalid exchange rate: {data_value}")
                continue
            
            # Domain Entity 생성
            ecos = Ecos(
                exchange_type=exchange_type,
                exchange_rate=exchange_rate,
                erm_date=erm_date,
                created_at=datetime.utcnow()
            )
            ecos_entities.append(ecos)
        
        # 3. Repository를 통해 배치 저장
        if ecos_entities:
            await self.repository.save_exchange_rates_batch(ecos_entities)
        
        return ecos_entities

    async def get_interest_rate(self) -> EcosData:
        return await self.adapter.get_interest_rate()

    async def fetch_and_save_interest_rate(self) -> List[EcosInterest]:
        """
        ECOS API에서 금리 데이터를 조회하고 데이터베이스에 저장한다.

        Returns:
            저장된 Ecos 도메인 엔티티 리스트
        """
        # 1. API에서 raw 데이터 조회
        from ecos.infrastructure.api.ecos_client import EcosClient
        client = EcosClient()
        raw_items = await client.get_interest_rate()

        # 2. Raw 데이터를 Domain Entity로 변환
        ecos_entities = []
        for item in raw_items:
            item_code = item.get('ITEM_CODE1')
            # TIME을 datetime으로 변환
            time_str = item.get('TIME')
            try:
                erm_date = datetime.strptime(time_str, '%Y%m%d')
            except (ValueError, TypeError):
                logger.warning(f"Invalid time format: {time_str}")
                continue

            data_value = item.get('DATA_VALUE')
            try:
                interest_rate = float(data_value)
            except (ValueError, TypeError):
                logger.warning(f"Invalid exchange rate: {data_value}")
                continue

            # Domain Entity 생성
            ecos = Ecos(
                exchange_type=item_code,
                exchange_rate=interest_rate,
                erm_date=erm_date,
                created_at=datetime.utcnow()
            )
            ecos_entities.append(ecos)

        # 3. Repository를 통해 배치 저장
        if ecos_entities:
            await self.repository.save_interest_rates_batch(ecos_entities)

        return ecos_entities