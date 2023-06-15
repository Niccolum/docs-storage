from typing import TYPE_CHECKING

from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from Secweb.ContentSecurityPolicy import (
    ContentSecurityPolicy,
)
from Secweb.ReferrerPolicy import ReferrerPolicy
from Secweb.StrictTransportSecurity import HSTS
from Secweb.XDNSPrefetchControl import (
    XDNSPrefetchControl,
)
from Secweb.XFrameOptions import XFrame
from Secweb.xXSSProtection import xXSSProtection
from starlette.middleware.cors import (
    CORSMiddleware,
)
from starlette_csrf.middleware import (
    CSRFMiddleware,
)

if TYPE_CHECKING:
    from fastapi import FastAPI

    from backend.settings.base import Settings


def set_middlewares(app: "FastAPI", settings: "Settings") -> None:
    _set_secure_middlewares(app=app, settings=settings)


def _set_secure_middlewares(app: "FastAPI", settings: "Settings") -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.security.cors_allow_origins],
        allow_credentials=settings.security.cors_allow_credentials,
        allow_methods=settings.security.cors_allow_methods,
        allow_headers=settings.security.cors_allow_headers,
    )

    app.add_middleware(
        CSRFMiddleware,
        secret=settings.security.csrf_secret_token.get_secret_value(),
        cookie_secure=settings.security.csrf_cookie_secure,
    )
    app.add_middleware(
        ContentSecurityPolicy,
        Option={
            "default-src": settings.security.csp_default_src,
            "script-src": settings.security.csp_script_src,
            "style-src": settings.security.csp_style_src,
            "base-uri": settings.security.csp_base_uri,
            "form-action": settings.security.csp_form_action,
            "block-all-mixed-content": settings.security.csp_block_all_mixed_content,
        },
        script_nonce=settings.security.csp_script_nonce,
        style_nonce=settings.security.csp_style_nonce,
    )
    app.add_middleware(ReferrerPolicy, Option={"Referrer-Policy": settings.security.referrer_policy})
    app.add_middleware(xXSSProtection, Option={"X-XSS-Protection": settings.security.x_xss_protection})
    app.add_middleware(XDNSPrefetchControl, Option={"X-DNS-Prefetch-Control": settings.security.x_dns_prefetch_control})
    app.add_middleware(XFrame, Option={"X-Frame-Options": settings.security.x_frame_options})

    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.security.trusted_hosts,
        www_redirect=settings.security.www_redirect,
    )

    if settings.security.https:
        app.add_middleware(HTTPSRedirectMiddleware)
        app.add_middleware(
            HSTS,
            Option={
                "max-age": int(settings.security.hsts_max_age.total_seconds()),
                "preload": settings.security.hsts_preload,
            },
        )
