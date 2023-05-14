import logging

from fastapi import FastAPI
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

from backend.api.router import api_router
from backend.settings.app import get_settings
from backend.settings.log import logging_setup

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    logging_setup()
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Authentication microservice for FellowMate ecosystem",
        version="0.0.1",
        externalDocs={
            "description": "See more docs about project",
            "url": "http://example.com",
        },
        openapi_url="/openapi.json",
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # add security middlewares
    app.add_middleware(
        CSRFMiddleware,
        secret=settings.secret_token,
        cookie_secure=settings.cookie_secure,
    )
    app.add_middleware(
        ContentSecurityPolicy,
        Option={
            "default-src": ["'self'"],
            "script-src": ["'self'"],
            "style-src": ["'self'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "block-all-mixed-content": [],
        },
        script_nonce=False,
        style_nonce=False,
    )
    app.add_middleware(ReferrerPolicy, Option={"Referrer-Policy": "strict-origin-when-cross-origin"})
    if settings.https:
        app.add_middleware(
            HSTS,
            Option={
                "max-age": 60
                * 60
                * 24
                * 365
                * 2,  # recommended value by https://hstspreload.org/#deployment-recommendations
                "preload": True,
            },
        )
    app.add_middleware(xXSSProtection, Option={"X-XSS-Protection": "1"})
    app.add_middleware(XDNSPrefetchControl, Option={"X-DNS-Prefetch-Control": "on"})
    app.add_middleware(XFrame, Option={"X-Frame-Options": "DENY"})

    app.include_router(api_router)

    return app
