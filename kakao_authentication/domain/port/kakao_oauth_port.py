from abc import ABC, abstractmethod

from kakao_authentication.domain.kakao_user import KakaoUser
from kakao_authentication.domain.value_objects.kakao_access_token import KakaoAccessToken


class KakaoOAuthPort(ABC):

    @abstractmethod
    def get_access_token(self, auth_code: str) -> KakaoAccessToken:
        pass

    @abstractmethod
    def get_user_info(self, access_token: KakaoAccessToken) -> KakaoUser:
        pass
