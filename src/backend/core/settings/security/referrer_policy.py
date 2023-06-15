from pydantic import BaseSettings


class ReferrerPolicySettings(BaseSettings):
    referrer_policy: str = "strict-origin-when-cross-origin"
