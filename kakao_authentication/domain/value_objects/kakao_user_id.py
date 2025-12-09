class KakaoUserId:
    def __init__(self, value: int):
        if value <= 0:
            raise ValueError("KakaoUserId must be positive")
        self._value = value

    @property
    def value(self) -> int:
        return self._value
