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
    _set_common_middlewares(app=app, settings=settings)


def _set_secure_middlewares(app: "FastAPI", settings: "Settings") -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.cors_allow_origins],
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    app.add_middleware(
        CSRFMiddleware,
        secret=settings.csrf_secret_token.get_secret_value(),
        cookie_secure=settings.csrf_cookie_secure,
    )
    app.add_middleware(
        ContentSecurityPolicy,
        Option={
            "default-src": settings.csp_default_src,
            "script-src": settings.csp_script_src,
            "style-src": settings.csp_style_src,
            "base-uri": settings.csp_base_uri,
            "form-action": settings.csp_form_action,
            "block-all-mixed-content": settings.csp_block_all_mixed_content,
        },
        script_nonce=settings.csp_script_nonce,
        style_nonce=settings.csp_style_nonce,
    )
    app.add_middleware(ReferrerPolicy, Option={"Referrer-Policy": settings.referrer_policy})
    app.add_middleware(xXSSProtection, Option={"X-XSS-Protection": settings.x_xss_protection})
    app.add_middleware(XDNSPrefetchControl, Option={"X-DNS-Prefetch-Control": settings.x_dns_prefetch_control})
    app.add_middleware(XFrame, Option={"X-Frame-Options": settings.x_frame_options})

    if settings.https:
        app.add_middleware(
            HSTS,
            Option={
                "max-age": int(settings.hsts_max_age.total_seconds()),
                "preload": settings.hsts_preload,
            },
        )


def _set_common_middlewares(app: "FastAPI", settings: "Settings") -> None:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.trusted_hosts,
        www_redirect=settings.www_redirect,
    )
    if settings.https:
        app.add_middleware(HTTPSRedirectMiddleware)
