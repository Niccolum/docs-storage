from pydantic_settings import BaseSettings


class xFrameSettings(BaseSettings):  # noqa: N801
    x_frame_options: str = "DENY"
