from kakao_authentication.domain.value_objects.kakao_email import KakaoEmail
from kakao_authentication.domain.value_objects.kakao_nickname import KakaoNickname
from kakao_authentication.domain.value_objects.kakao_user_id import KakaoUserId


class KakaoUser:
    def __init__(
        self,
        user_id: KakaoUserId,
        email: KakaoEmail,
        nickname: KakaoNickname
    ):
        self.user_id = user_id
        self.email = email
        self.nickname = nickname
