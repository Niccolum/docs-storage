from typing import ClassVar

from pydantic_settings import BaseSettings


class CspSettings(BaseSettings):
    csp_default_src: ClassVar[list[str]] = ["'self'"]
    csp_script_src: ClassVar[list[str]] = ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"]
    csp_style_src: ClassVar[list[str]] = ["'self'", "cdn.jsdelivr.net"]
    csp_base_uri: ClassVar[list[str]] = ["'self'"]
    csp_form_action: ClassVar[list[str]] = ["'self'"]
    csp_block_all_mixed_content: ClassVar[list[str]] = []
    csp_img_src: ClassVar[list[str]] = ["'self'", "data:", "fastapi.tiangolo.com"]

    csp_script_nonce: bool = False
    csp_style_nonce: bool = False
