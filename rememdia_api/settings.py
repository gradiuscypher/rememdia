from enum import Enum
from os import environ

from dotenv import load_dotenv

load_dotenv()

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


DISCORD_WEBHOOK = environ.get("REM_DISCORD_WEBHOOK")
REMINDER_INTERVAL = int(environ.get("REM_REMINDER_INTERVAL", 30))
READING_INTERVAL = int(environ.get("REM_READING_INTERVAL", 30))