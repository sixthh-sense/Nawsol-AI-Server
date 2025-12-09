class KakaoRefreshToken:
    def __init__(self, value: str):
        if not value:
            raise ValueError("RefreshToken cannot be empty")
        self._value = value

    @property
    def value(self) -> str:
        return self._value
