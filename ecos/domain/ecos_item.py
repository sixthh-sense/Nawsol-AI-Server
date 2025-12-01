from datetime import datetime

class EcosItem:
    def __init__(self, item_type:str, time: datetime, value: float):
        self.item_type = item_type
        self.time = time
        self.value = value
