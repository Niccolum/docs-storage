from pydantic import (
    root_validator,  # pyright: ignore reportUnknownVariableType
)

from backend.settings.base import SettingsConfigMixin

from .cors import CorsSettings
from .csp import CspSettings
from .csrf import CsrfSettings
from .hsts import HSTSSettings
from .referrer_policy import ReferrerPolicySettings
from .trusted_host import TrustedHostSettings
from .x_dns import xDNSSettings
from .x_frame import xFrameSettings
from .x_xss import xXSSSettings


class WebSecureSettings(
    CorsSettings,
    CspSettings,
    CsrfSettings,
    HSTSSettings,
    ReferrerPolicySettings,
    xDNSSettings,
    xFrameSettings,
    xXSSSettings,
    TrustedHostSettings,
):
    https: bool

    class Config(SettingsConfigMixin):
        env_prefix = "SECURITY_"
