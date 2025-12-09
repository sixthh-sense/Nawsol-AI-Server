class KakaoNickname:
    def __init__(self, value: str):
        if not value or not value.strip():
            raise ValueError("Kakao Nickname cannot be empty")

        if len(value) > 20:
            raise ValueError("Kakao Nickname is too long")

        self.value = value.strip()

    def __str__(self):
        return self.value
