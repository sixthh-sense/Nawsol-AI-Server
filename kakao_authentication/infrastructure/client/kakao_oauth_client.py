import requests

from kakao_authentication.domain.kakao_user import KakaoUser
from kakao_authentication.domain.port.kakao_oauth_port import KakaoOAuthPort
from kakao_authentication.domain.value_objects.kakao_access_token import KakaoAccessToken
from kakao_authentication.domain.value_objects.kakao_email import KakaoEmail
from kakao_authentication.domain.value_objects.kakao_nickname import KakaoNickname
from kakao_authentication.domain.value_objects.kakao_user_id import KakaoUserId
from config.env import (
    KAKAO_CLIENT_ID,
    KAKAO_REDIRECT_URI,
    KAKAO_SECRET_KEY
)
from util.log.log import Log
KAKAO_TOKEN_URL = "https://kauth.kakao.com/oauth/token"
KAKAO_USER_URL = "https://kapi.kakao.com/v2/user/me"

log_util = Log()
logger = Log.get_logger()
class KakaoOAuthClient(KakaoOAuthPort):

    def get_access_token(self, auth_code: str) -> KakaoAccessToken:
        data = {
            "grant_type": "authorization_code",
            "client_id": KAKAO_CLIENT_ID,
            "redirect_uri": KAKAO_REDIRECT_URI,
            "code": auth_code,
            "client_secret": KAKAO_SECRET_KEY
        }

        response = requests.post(
            KAKAO_TOKEN_URL,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )

        response.raise_for_status()

        token = response.json()["access_token"]
        return KakaoAccessToken(token)

    def get_user_info(self, token: KakaoAccessToken) -> KakaoUser:
        url = "https://kapi.kakao.com/v2/user/me"

        headers = {
            "Authorization": f"Bearer {token.value}"
        }

        response = requests.get(url, headers=headers)
        json_data = response.json()
        print(json_data)

        user_id = KakaoUserId(json_data["id"])
        email = KakaoEmail(json_data["kakao_account"].get("email"))
        nickname = KakaoNickname(json_data["properties"]["nickname"])

        return KakaoUser(user_id, email, nickname)

