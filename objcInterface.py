from AppKit import NSPasteboard
import time
from loguru import logger
import AppKit
from PyObjCTools.AppHelper import runEventLoop


class ClipboardListener:
    def __init__(self):
        self.pasteboard = NSPasteboard.generalPasteboard()
        self.last_change_count = self.pasteboard.changeCount()
        self.poll_interval = 0.5  # 初始轮询间隔

    def listen(self, ontrigger):
        logger.debug("Snaptask starts listening to clipboard changes...")
        while True:
            # 检查 changeCount 是否发生变化
            current_change_count = self.pasteboard.changeCount()
            if current_change_count != self.last_change_count:
                logger.debug("Clipboard changed")
                self.last_change_count = current_change_count

                # 获取新剪切板内容
                content = self.pasteboard.stringForType_("public.utf8-plain-text")
                if content:
                    logger.debug("New clipboard content detected", content)
                    try:
                        ontrigger(content)
                    except Exception as e:
                        logger.error(
                            f"Unexpected error occurred while processing clipboard content:{e}"
                        )

            # 轮询间隔
            time.sleep(self.poll_interval)
