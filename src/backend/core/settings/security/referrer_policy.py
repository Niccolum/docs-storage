from pydantic_settings import BaseSettings


class ReferrerPolicySettings(BaseSettings):
    referrer_policy: str = "strict-origin-when-cross-origin"
