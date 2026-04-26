import logging
import asyncio
from typing import Dict, Any
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from app.services.vector_service import vector_service
from app.config import settings
import os

os.environ["DASHSCOPE_API_KEY"] = settings.TONGYI_API_KEY

logger = logging.getLogger("documind.agent")


class AgentService:
    def __init__(self):
        try:
            # 初始化与 llm_service 类似，使用 ChatTongyi
            self.chat_model = ChatTongyi(model_name="qwen-turbo")
            self.session_memories: Dict[str, ConversationSummaryBufferMemory] = {}
            logger.info("AgentService LLM (ChatTongyi) 初始化成功")
        except Exception as e:
            logger.error(f"AgentService LLM 初始化异常: {str(e)}")
            self.chat_model = None

    def get_memory(self, session_id: str) -> ConversationSummaryBufferMemory:
        """
        获取带有摘要能力的Agent记忆上下文
        """
        if session_id not in self.session_memories:
            self.session_memories[session_id] = ConversationSummaryBufferMemory(
                llm=self.chat_model,
                max_token_limit=3000,
                memory_key="chat_history",  # 匹配 Prompt 里的占位符
                return_messages=False,
                input_key="input",  # 匹配 AgentExecutor 要求的用户输入字段
            )
        return self.session_memories[session_id]

    async def generate_deep_discuss(
        self, query: str, session_id: str, doc_id: str
    ) -> dict:
        """
        Day 4 任务核心：执行带深层次研讨能力的 Agent 问答逻辑。
        由智能体来自主决定需要几次文档检索，何时提取文档原文引用去思考和综合。
        """
        if not self.chat_model:
            raise ValueError("AgentService LLM 模型未就绪。请检查环境变量。")

        # 为了每次请求挂载动态的 doc_id，我们使用闭包生成 Retriever 工具函数
        async def _arun_retriever(search_query: str) -> str:
            # 异步执行文档内容检索
            try:
                docs = await vector_service.similarity_search(
                    query=search_query, k=5, doc_id=doc_id
                )
                if not docs:
                    return "当前文档中未检索到明确相关的内容片段。"
                res = []
                for i, d in enumerate(docs):
                    res.append(f"【引用片段{i+1}】:\n{d.page_content}")
                return "\n\n".join(res)
            except Exception as e:
                logger.error(f"Agent 文档检索失败: {e}")
                return f"由于系统异常，检索文档失败：{str(e)}"

        def _run_retriever(search_query: str) -> str:
            # Langchain 的 AgentExecutor 如果处于同步执行降级时会被调用
            return asyncio.run(_arun_retriever(search_query))

        # 配置对大模型公开的检索工具箱
        retrieval_tool = Tool(
            name="Doc_Retriever",
            description="当需要结合上传的文档原文或数据来回答时，必须调用此工具。输入最好是一句完整的陈述事实或核心疑问句，以提升召回率。",
            func=_run_retriever,
            coroutine=_arun_retriever,
        )

        tools = [retrieval_tool]

        # =======================================================
        # 【Day 4 智能体 Agent 提示词工程 (ReAct)】
        # 赋予角色设定，给出研讨和分析的模板，强调使用正确的动作链来与用户交互
        # =======================================================
        template = """你是一个高阶的文档研讨AI助手（DocuMind Agent）。你的任务是通过主动多次思考、反复检索原文、总结提炼，深层次地回答该文档相关的问题，并给出具有洞察力的分析。
你拥有以下工具来帮助你挖掘文档中隐藏的信息：

{tools}

如果被问及你不清楚的文档内容，或者需要结合具体案例分析，请你坚决调用检索工具来收集线索。不要凭空捏造。

请必须严格且始终遵循以下输出的思考和调用格式流程回答：
---
Question: 需要你回答的用户问题或指令
Thought: 你应该思考目前掌握的信息是否够用，以及拆解这个问题是否需要查阅文档信息
Action: 需要执行的动作，必须是 [{tool_names}] 中的一个字典名（不用写大括号），如不需要动作这步则跳过
Action Input: 发送给动作的输入参数，请提供清晰具体的查询短语
Observation: 动作返回的文档引用或结果内容
...（上述 Thought/Action/Action Input/Observation 的观察循环可以重复多次）
Thought: 我现在已经掌握了所有事实，我知道最终的深层次分析与研讨结论了
Final Answer: 输出最后详尽、有深度见解的分析（在最终回答里你可以列举数据并引出你的观点）。
---

对话历史（参考上下文）：
{chat_history}

Question: {input}
Thought: {agent_scratchpad}"""

        prompt = PromptTemplate.from_template(template)

        # 构建 Agent
        # create_react_agent 负责将提示模板与模型关联输出解析链
        agent = create_react_agent(llm=self.chat_model, tools=tools, prompt=prompt)

        # 获取历史上下文
        memory = self.get_memory(session_id)

        # 配置具备错误处理、重试功能的 Agent 执行循环 (Agent Architecture)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            handle_parsing_errors="你的输出格式有误导致无法解析。必须严格按照 'Thought: ... \nAction: ... \nAction Input: ...' 或直接以 'Final Answer: xxx' 结束。",
            max_iterations=6,  # 为了避免模型卡在死循环中
            early_stopping_method="generate",
        )

        try:
            # 执行智能体的深层次问答
            response = await agent_executor.ainvoke({"input": query})
            # Langchain ReAct executor默认把最终输出放在 'output' 下
            answer = response.get("output", "Agent 未能有效组织语言回答。")
            return {"answer": answer}
        except Exception as e:
            logger.error(f"AgentExecutor 核心运行阶段异常: {str(e)}")
            raise e


# 提供一个全局可用的实例
agent_service = AgentService()
