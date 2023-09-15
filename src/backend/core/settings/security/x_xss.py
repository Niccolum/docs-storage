from pydantic_settings import BaseSettings


class xXSSSettings(BaseSettings):  # noqa: N801
    x_xss_protection: str = "1"
