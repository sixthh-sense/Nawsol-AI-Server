from abc import ABC, abstractmethod
from typing import List

from ecos.domain.ecos_item import EcosItem


class EcosDataApiPort(ABC):
    @abstractmethod
    async def get_exchange_rate(self) -> List[EcosItem]:
        pass