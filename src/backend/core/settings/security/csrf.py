from pydantic import SecretStr
from pydantic_settings import BaseSettings


class CsrfSettings(BaseSettings):
    csrf_secret_token: SecretStr
    csrf_cookie_secure: bool = False
