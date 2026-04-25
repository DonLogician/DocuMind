import os
import logging
from typing import Optional
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    def __init__(self):
        # 初始化通义千问模型
        # LangChain 默认从环境变量 DASHSCOPE_API_KEY 中读取密钥
        if settings.TONGYI_API_KEY:
            os.environ["DASHSCOPE_API_KEY"] = settings.TONGYI_API_KEY

        try:
            self.chat_model = ChatTongyi(
                model_name=settings.TONGYI_MODEL,
                temperature=0.7,
                # 可以在这里添加更多的模型参数
            )
            logger.info(f"成功初始化通义千问模型：{settings.TONGYI_MODEL}")
        except Exception as e:
            logger.error(
                f"初始化通义千问模型失败，请检查 TONGYI_API_KEY 设置: {str(e)}"
            )
            self.chat_model = None

    async def generate_basic_chat(self, query: str) -> str:
        """
        处理基础的无记忆单轮对话
        """
        if not self.chat_model:
            raise ValueError("LLM 模型未正确初始化，请检查 API KEY。")

        messages = [
            SystemMessage(
                content="你是一个专门用于智能文档研讨的AI助手 DocuMind。请回答用户的问题，保持专业和简洁。"
            ),
            HumanMessage(content=query),
        ]

        try:
            # 异步调用模型
            response = await self.chat_model.ainvoke(messages)
            return response.content
        except Exception as e:
            logger.error(f"调用通义千问 API 发生错误: {str(e)}")
            raise e


# 实例化全局服务
llm_service = LLMService()
