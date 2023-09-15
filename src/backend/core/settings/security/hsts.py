import datetime as dt

from pydantic_settings import BaseSettings


class HSTSSettings(BaseSettings):
    hsts_max_age: dt.timedelta = dt.timedelta(days=365 * 2)
    hsts_preload: bool = True
