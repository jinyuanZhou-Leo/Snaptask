from zhipuai import ZhipuAI
from loguru import logger
import sys
import time
import os
from utils import *
from pathlib import Path
from dotenv import load_dotenv
from Chat import Chat
from ClipboardListener import ClipboardListener

load_dotenv()
APIKEY: str | None = os.getenv("ZHIPU_API_KEY")
MODEL: str = "glm-4-flash"
VERSION = "1.0.0"
logger.remove()
logger.add(sys.stdout, level="DEBUG", colorize=True)
logger.info(f"Snaptask v{VERSION}")
with Path("./system_prompt.md").open() as f:
    system_prompt = f.read()


def throttle(wait_time):
    def decorator(func):
        last_call_time = [0.0]

        def throttled_func(*args, **kwargs):
            current_time = time.time()
            if (current_time - last_call_time[0]) >= wait_time:
                func(*args, **kwargs)
                last_call_time[0] = current_time

        return throttled_func

    return decorator


@throttle(2)
def extract_task(prompt) -> None:

    chat = Chat(
        client,
        system_prompt=system_prompt,
        stream=False,
        model=MODEL,
    )
    response: str = chat.getStringResponse(prompt)

    logger.info(f"Response: {response}")


if not APIKEY:
    logger.warning(".env Configuration not found")
    APIKEY = input("Please enter your Zhipu AI API Key: ").strip()
    setEnvVar("ZHIPU_API_KEY", APIKEY)
    logger.debug("API Key has been cached")
else:
    logger.success(f"API Key loaded: {APIKEY[:10]}...{APIKEY[40:]}")  # 部分显示,保护隐私

try:
    client = ZhipuAI(api_key=APIKEY)
except Exception as e:
    logger.critical(f"Failed to initialize ZhipuAI client: {e}")
    setEnvVar("ZHIPU_API_KEY", "")
    exit(0)

# 启动监听
listener = ClipboardListener()
listener.listen(ontrigger=extract_task)
