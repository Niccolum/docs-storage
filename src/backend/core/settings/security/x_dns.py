from pydantic_settings import BaseSettings


class xDNSSettings(BaseSettings):  # noqa: N801
    x_dns_prefetch_control: str = "on"
