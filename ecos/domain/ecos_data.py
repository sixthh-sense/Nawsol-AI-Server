from typing import List

from ecos.domain.ecos_item import EcosItem
from ecos.domain.value_object.ecos_source import EcosSource
from .value_object.timestamp import Timestamp

class EcosData:
    def __init__(self, items: List[EcosItem], source: EcosSource, fetched_at: Timestamp):
        self.items = items
        self.source = source
        self.fetched_at = fetched_at

    def add_item(self, item: EcosItem):
        self.items.append(item)