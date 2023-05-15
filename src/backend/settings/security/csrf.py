from pydantic import (
    BaseSettings,
    SecretStr,  # pyright: ignore reportUnknownVariableType
)


class CsrfSettings(BaseSettings):
    csrf_secret_token: SecretStr
    csrf_cookie_secure: bool = False
