from zhipuai import ZhipuAI
from dotenv import load_dotenv
from loguru import logger

load_dotenv()


class Chat:
    def __init__(
        self,
        client: ZhipuAI,
        system_prompt: str = "",
        context: list[dict[str, str]] = None,
        top_p: float = 0.5,
        temperature: float = 0.5,
        max_tokens: int = 2048,
        stream: bool = False,
        model: str = "glm-4-flash",
    ) -> None:
        """
        初始化 Chat 类实例。

        :param api_key: ZhipuAI API 密钥
        :param system_prompt: 系统提示
        :param context: 上下文列表
        :param top_p: 核心采样概率
        :param temperature: 温度参数
        :param max_tokens: 最大生成 token 数量
        :param stream: 是否启用流式响应
        :param model: 使用的模型名称
        """
        self.client = client
        self.context = context if context is not None else []
        self.top_p = top_p
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stream = stream
        self.model = model

        # logger.debug(f"System prompt: {system_prompt}, Context: {self.context}")

        if system_prompt and context:
            logger.error("System prompt is only available when there is NO context given")
            raise ValueError

        if system_prompt:
            self.context.append({"role": "system", "content": system_prompt})

    def __getResponse(self, prompt: str):
        self.context.append(
            {
                "role": "user",
                "content": f"{prompt}",
            }
        )

        return self.client.chat.completions.create(
            model=self.model,
            messages=self.context,
            top_p=self.top_p,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            stream=self.stream,
        )

    def getStringResponse(self, prompt: str) -> str:  # type: ignore
        if not self.stream:
            response: str = self.__getResponse(prompt).choices[0].message.content
            self.context.append(
                {
                    "role": "assistant",
                    "content": response,
                }
            )
            return response
        else:
            logger.error("Stream response cannot be converted to string")
            raise ValueError
