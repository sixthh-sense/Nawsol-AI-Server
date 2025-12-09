from account.adapter.input.web.request.create_account_request import CreateAccountRequest
from account.application.usecase.account_usecase import AccountUseCase
from config.env import KAKAO_CLIENT_ID, KAKAO_REDIRECT_URI
from kakao_authentication.domain.kakao_user import KakaoUser
from kakao_authentication.domain.port.kakao_oauth_port import KakaoOAuthPort
from kakao_authentication.domain.value_objects.kakao_authorization_url import KakaoAuthorizationUrl
from sosial_oauth.adapter.input.web.response.access_token import AccessToken

account_usecase = AccountUseCase().get_instance()

class KakaoOAuthUseCase:

    def __init__(self, kakao_oauth_port: KakaoOAuthPort):
        self.kakao_oauth_port = kakao_oauth_port

    def get_authorization_url(self) -> str:
        auth_url = KakaoAuthorizationUrl(
            client_id=KAKAO_CLIENT_ID,
            redirect_uri=KAKAO_REDIRECT_URI
        )

        return str(auth_url)

    def get_kakao_user(self, code: str) -> dict:
        access_token: AccessToken = self.kakao_oauth_port.get_access_token(code)
        kakao_user: KakaoUser = self.kakao_oauth_port.get_user_info(access_token)

        return {
            "user": kakao_user,
            "access_token": access_token.value
        }

    async def create_or_get_account(self, kakao_user: KakaoUser, session_id: str) -> str:
        sso_id = kakao_user.user_id.value
        if not sso_id:
            raise ValueError("User profile does not contain 'sub' or 'id' field")

        existing_account = account_usecase.get_account_by_oauth_id("KAKAO", sso_id)

        print(f"[DEBUG] Existing account: {existing_account}")
        if existing_account:
            # 기존 계정이 있는 경우, 변경된 필드만 업데이트
            self._update_account_if_changed(existing_account, kakao_user)
            session_id = existing_account.session_id
        else:
            # 새 계정 생성
            await self._create_new_account(kakao_user, str(sso_id), session_id)

        return session_id

    @staticmethod
    def _update_account_if_changed(existing_account, user_profile: KakaoUser) -> None:
        # 기존 계정의 정보가 변경된 경우에만 업데이트
        email = user_profile.email.value or ""
        nickname = user_profile.nickname.value or ""

        # 변경된 필드가 있는지 확인
        has_changes = (
                existing_account.email != email or
                existing_account.nickname != nickname
        )

        if has_changes:
            update_request = CreateAccountRequest(
                oauth_id=existing_account.oauth_id,
                oauth_type=existing_account.oauth_type,
                nickname=nickname,
                name=existing_account.name,
                profile_image=existing_account.profile_image,
                email=email,
                phone_number=existing_account.phone_number,
                active_status=existing_account.active_status,
                role_id=existing_account.role_id,
            )
            account_usecase.update(update_request)

    @staticmethod
    async def _create_new_account(user_profile: KakaoUser, sso_id: str, session_id: str) -> None:
        # 새로운 계정을 생성
        await account_usecase.create_account(
            session_id=session_id,
            oauth_id=sso_id,
            oauth_type="KAKAO",
            nickname=user_profile.nickname.value or "",
            name="",
            profile_image="",
            email=user_profile.email.value or "",
            phone_number="",
            active_status="Y",
            role_id=""
        )
