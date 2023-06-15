from pydantic import BaseSettings


class TrustedHostSettings(BaseSettings):
    trusted_hosts: list[str]
    www_redirect: bool = False
