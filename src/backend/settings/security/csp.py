from pydantic import BaseSettings


class CspSettings(BaseSettings):
    csp_default_src: list[str] = ["'self'"]
    csp_script_src: list[str] = ["'self'"]
    csp_style_src: list[str] = ["'self'"]
    csp_base_uri: list[str] = ["'self'"]
    csp_form_action: list[str] = ["'self'"]
    csp_block_all_mixed_content: list[str] = []

    csp_script_nonce: bool = False
    csp_style_nonce: bool = False
