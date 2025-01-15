from zhipuai import ZhipuAI
from loguru import logger
import sys
import time
import platform
import os
import threading
import pyperclip
from utils import *
from pathlib import Path
from dotenv import load_dotenv
from Chat import Chat
from pynput import keyboard

load_dotenv()
APIKEY = os.getenv("ZHIPU_API_KEY")
MODEL: str = "glm-4-airx"
VERSION = "1.0.0"
logger.info(f"Snaptask v{VERSION}")
with Path("./system_prompt.md").open() as f:
    system_prompt = f.read()

# 初始化日志记录器
logger.remove()
logger.add(sys.stderr, level="DEBUG", colorize=True)

# 获取平台信息
platform_name = platform.system()

if platform_name == "Windows":
    logger.debug("检测到Windows平台")
    COPY = {keyboard.Key.ctrl, keyboard.KeyCode.from_char('c')}
    #PASTE = {keyboard.Key.ctrl, keyboard.KeyCode.from_char('v')}
elif platform_name == "Darwin":
    logger.debug("检测到Mac平台")
    COPY = {keyboard.Key.cmd, keyboard.KeyCode.from_char('c')}
    #PASTE = {keyboard.Key.cmd, keyboard.KeyCode.from_char('v')}
else:
    logger.critical("不支持的平台")
    sys.exit(0)

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
def extract_task(prompt:str) -> None:

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

# 线程锁
current_keys_lock = threading.Lock()
current_clipboard_lock = threading.Lock()
current_keys = set()
current_clipboard = ""

def on_press(key):
    with current_keys_lock:
        current_keys.add(key)
        logger.debug(f"键按下! 当前按键: {current_keys}")
        if check_combination(current_keys, COPY):
            logger.success("检测到复制操作")
            with current_clipboard_lock:
                global current_clipboard
                current_clipboard = pyperclip.paste()
                logger.debug(f"剪贴板: {current_clipboard}")
            logger.info("Stop listening to keyboard events...")
            listener.stop()

def on_release(key):
    with current_keys_lock:
        try:
            current_keys.remove(key)
            logger.debug(f"键释放! 当前按键: {current_keys}")
        except KeyError:
            logger.warning(f"尝试移除一个不在集合中的键: {key}")

def check_combination(current: set, combination: set) -> bool:
    logger.debug(f"检查组合: {combination} 当前按键: {current}")
    if combination == current:
        logger.debug(f"检测到组合: {combination}!")
        return True
    else:
        return False

while True:
    current_keys = set()
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        logger.info("Start listening to keyboard events...")
        listener.join()
    extract_task(current_clipboard)
