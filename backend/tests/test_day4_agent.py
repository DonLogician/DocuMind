import asyncio
from app.services.vector_service import vector_service
from app.services.agent_service import agent_service
from langchain.text_splitter import RecursiveCharacterTextSplitter
import sys


# 重定向 stdout 和 stderr 到 output.txt
class LoggerWriter:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.file = open(filename, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)

    def flush(self):
        self.terminal.flush()
        self.file.flush()


def setup_logger():
    # Only map stdout/stderr once
    logger = LoggerWriter("output.txt")
    sys.stdout = logger
    sys.stderr = logger


async def main():
    print("=" * 50)
    print("开始 Day 4 研讨型 Agent 能力测试")
    print("=" * 50)

    doc_id = "test_article_doc4"

    print("\n[步骤 1] 读取并分块入库 test_article.txt...")
    try:
        with open("test_article.txt", "r", encoding="utf-8") as f:
            text = f.read()

        # 分块后入库
        splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=150)
        chunks = splitter.split_text(text)

        await vector_service.add_documents(
            chunks=chunks, metadata={"doc_id": doc_id, "source": "test_article.txt"}
        )
        print(f"入库完成，共 {len(chunks)} 块段落。")
    except Exception as e:
        print(f"数据入库遇到问题: {e}")

    session_id = "agent_test_session_002"

    questions = [
        {
            "type": "客观信息问题 1",
            "q": "这家裁缝店开在哪里？当地人的体格有什么特点导致他们更需要裁缝量身定做？",
        },
        {
            "type": "客观信息问题 2",
            "q": "老裁缝家比'小上海'家收费贵，但为什么生意更好？他们在裤子加工细节上有什么具体区别？",
        },
        {
            "type": "客观信息问题 3",
            "q": "漂亮的库尔马罕儿媳妇来做裙子时，用了什么当定金？当时她和婆婆是怎么商量的？",
        },
        {
            "type": "主观赏析问题 1",
            "q": "文章后半部分提到'马蹄袖'是怎么由来的？这个带有点戏剧性的失误和解决过程，表现了母女俩怎样的人生态度？",
        },
        {
            "type": "主观赏析问题 2",
            "q": "阅读全文，作者对待裁缝这份辛劳的工作持有怎样复杂的情感？结合'一针一线拆不掉'这句话谈谈你的理解。",
        },
    ]

    print("\n[步骤 2] 向 Agent 提出问题，启动 ReAct 检索和思考过程：\n")

    for i, item in enumerate(questions):
        print(f"\n{'='*50}")
        print(f"【测试轮次 {i+1}】 - {item['type']}")
        print(f"【用户提问】: {item['q']}")
        print(f"{'='*50}\n")

        try:
            res = await agent_service.generate_deep_discuss(
                query=item["q"], session_id=session_id, doc_id=doc_id
            )
            print("\n" + "*" * 40)
            print("[Agent 最终给出的回答]:")
            print("*" * 40)
            print(res["answer"])
        except Exception as e:
            print(f"\n[Agent 执行异常]: {str(e)}")

    print("\n" + "=" * 50)
    print("Day 4 测试完成。结果已保存在 output.txt 中。")
    print("=" * 50)


if __name__ == "__main__":
    setup_logger()
    asyncio.run(main())
