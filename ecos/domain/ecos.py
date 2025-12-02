from datetime import datetime

from ecos.infrastructure.orm.exchange_rate import ExchangeType


class Ecos:
    def __init__(self, exchange_type: ExchangeType, exchange_rate: float, erm_date: datetime, created_at: datetime):
        self.exchange_type = exchange_type
        self.exchange_rate = exchange_rate
        self.erm_date = erm_date
        self.created_at = created_at