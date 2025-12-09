class KakaoEmail:
    def __init__(self, value: str):
        if "@" not in value:
            raise ValueError("Invalid email format")
        self._value = value

    @property
    def value(self) -> str:
        return self._value
