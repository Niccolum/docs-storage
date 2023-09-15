
from pydantic import AnyHttpUrl, computed_field
from pydantic_settings import SettingsConfigDict

from backend.core.settings.base import env_file

from .cors import CorsSettings
from .csp import CspSettings
from .csrf import CsrfSettings
from .file_encryption import FileEncryptionSettings
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
    FileEncryptionSettings,
):
    https: bool
    app_port: int

    model_config = SettingsConfigDict(env_prefix="SECURITY_", env_file=env_file, extra="allow")

    @computed_field
    def cors_allow_origins(self) -> list[AnyHttpUrl]:
        result: list[AnyHttpUrl] = []
        scheme = "https" if self.https else "http"
        data = []

        for raw_host in self.cors_hosts:
            host_url = AnyHttpUrl.build(host=raw_host, port=self.app_port, scheme=scheme)
            data.append(host_url)

        return result
