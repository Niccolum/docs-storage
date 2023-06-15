from pydantic import BaseSettings


class CspSettings(BaseSettings):
    csp_default_src: list[str] = ["'self'"]
    csp_script_src: list[str] = ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"]
    csp_style_src: list[str] = ["'self'", "cdn.jsdelivr.net"]
    csp_base_uri: list[str] = ["'self'"]
    csp_form_action: list[str] = ["'self'"]
    csp_block_all_mixed_content: list[str] = []
    csp_img_src: list[str] = ["'self'", "data:", "fastapi.tiangolo.com"]

    csp_script_nonce: bool = False
    csp_style_nonce: bool = False
