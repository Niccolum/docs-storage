from pydantic import BaseSettings

from .cors import CorsSettings
from .csp import CspSettings
from .csrf import CsrfSettings
from .hsts import HSTSSettings
from .referrer_policy import ReferrerPolicySettings
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
):
    class Config(BaseSettings.Config):  # pyright: ignore reportIncompatibleVariableOverride
        env_prefix = ""
