from enum import Enum
from os import environ


class EnvironmentEnum(Enum):
    TEST = "test"
    DEV = "dev"
    PROD = "prod"


if environ.get("REM_ENV") == "test":
    ENVIRONMENT = EnvironmentEnum.TEST
elif environ.get("REM_ENV") == "prod":
    ENVIRONMENT = EnvironmentEnum.PROD
else:
    ENVIRONMENT = EnvironmentEnum.DEV
