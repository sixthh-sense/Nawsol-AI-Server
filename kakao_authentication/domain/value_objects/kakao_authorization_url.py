class KakaoAuthorizationUrl:
    BASE_URL = "https://kauth.kakao.com/oauth/authorize"

    def __init__(self, client_id: str, redirect_uri: str):
        if not client_id:
            raise ValueError("Kakao client_id is required")

        if not redirect_uri:
            raise ValueError("Kakao redirect_uri is required")

        self.client_id = client_id
        self.redirect_uri = redirect_uri

    def build(self) -> str:
        return (
            f"{self.BASE_URL}"
            f"?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&response_type=code"
        )

    def __str__(self):
        return self.build()
