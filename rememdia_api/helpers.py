import logging
import httpx

from bs4 import BeautifulSoup
from bs4.element import Tag

from settings import DISCORD_WEBHOOK


client = httpx.AsyncClient(follow_redirects=True)


def configure_logging(logger_name: str = __name__) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    stream_handle = logging.StreamHandler()
    stream_handle.setFormatter(formatter)
    file_handle = logging.FileHandler("rememdia.log")
    file_handle.setFormatter(formatter)

    logger.addHandler(stream_handle)
    logger.addHandler(file_handle)

    logger.setLevel(logging.DEBUG)

    return logger


logger = configure_logging()


async def get_link_metadata(url: str) -> tuple[str, str]:
    """
    Parse the page with beautifulsoup and provide metadata about the link
    https://www.reddit.com/r/discordapp/comments/82p8i6/a_basic_tutorial_on_how_to_get_the_most_out_of/
    """
    try:
        if not url.startswith("http"):
            url = f"https://{url}"

        result = await client.get(url)
        soup = BeautifulSoup(result.content, "html.parser")

        description = soup.find("meta", property="og:description")
        description = (
            str(description.get("content")) if isinstance(description, Tag) else ""
        )

        title = soup.find("meta", property="og:title")
        title = str(title.get("content")) if isinstance(title, Tag) else ""

    except Exception as exc:
        logger.exception("Error while fetching page metadata", exc_info=exc)
        return "", ""

    else:
        return title, description


async def send_discord_message(message: str):
    if not DISCORD_WEBHOOK:
        logger.warning("No discord webhook found")
        return

    try:
        webhook_embed = {
            "title": "Rememdia",
            "description": message,
            "color": 0x00ff00,
        }
        await client.post(DISCORD_WEBHOOK, json={"embeds": [webhook_embed]})
    except Exception as exc:
        logger.exception("Error while sending discord message", exc_info=exc)
