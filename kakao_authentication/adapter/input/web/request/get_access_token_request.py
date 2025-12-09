from pydantic import BaseModel

class GetAccessTokenRequest(BaseModel):
    auth_code: str
