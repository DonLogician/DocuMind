import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pprint import pprint

from app.services.document_parser import parse_document
from app.utils.text_utils import split_text_into_chunks
from app.services.vector_service import vector_service


async def run_tests():
    print("--- 开始测试 Day2 任务模块 ---")

    # 模拟待处理长文本
    raw_text = (
        "机器学习是一门多领域交叉学科，涉及概率论、统计学、逼近论、凸分析、算法复杂度理论等多门学科。\n"
        "专门研究计算机怎样模拟或实现人类的学习行为，以获取新的知识或技能，重新组织已有的知识结构使之不断改善自身的性能。\n"
        "它是人工智能的核心，是使计算机具有智能的根本途径，其应用遍及人工智能的各个领域，它主要使用归纳、综合而不是演绎。"
    ) * 5  # 放大长度为了使其超越 500 个字从而看分块表现

    # 1. 文本分块优化测试
    print("\n[测试] 文本分块工具 (RecursiveCharacterTextSplitter)")
    chunks = split_text_into_chunks(
        raw_text, chunk_size=300, chunk_overlap=50
    )  # 刻意缩小以便切分多块

    print(f"原始字数: {len(raw_text)} -> 切分成块数: {len(chunks)}")
    for i, c in enumerate(chunks[:2]):
        print(f" [Chunk {i}] ({len(c)} 字): {c[:50]}...")

    print("\n[测试] 向量化模型集成与数据库入库")

    if vector_service.vector_store is None:
        print("[跳过] Chroma 服务未初始化，请检查环境变量和文件权限。")
        return

    doc_meta = {
        "doc_id": "test_day2_doc_001",
        "filename": "机器学习概论.txt",
        "extension": ".txt",
    }

    try:
        # 入库测试 (包含了 Embedding 模型调用)
        await vector_service.add_documents(chunks, doc_meta)
        print(" -> 入库成功!")

        # 2. 检索器优化：执行核心相似度查询
        print("\n[测试] 检索器查询并验证语义相似度...")
        query = "计算机是如何获取知识并且实现人工智能的？"

        # 使用 MMR 参数
        results = await vector_service.similarity_search(query, k=2, use_mmr=True)

        print(f"搜索句子 '{query}' 得到相关结果 {len(results)} 个:")
        for r in results:
            meta = r.metadata
            print(
                f" [Chunk ID: {meta.get('chunk_index')}] - [{meta.get('filename')}] 摘录: {r.page_content[:60]}..."
            )

    except Exception as e:
        print(f"\n[错误] Day 2 功能集成发生故障: {str(e)}")
    finally:
        # 清理测试假数据
        print("\n[清理] 执行环境清理撤销刚才加入的分片...")
        deleted = await vector_service.delete_document("test_day2_doc_001")
        if deleted:
            print(" -> 撤销和清理恢复成功。")

    print("\n--- Day2 任务模块全部测试完毕 ---")


if __name__ == "__main__":
    asyncio.run(run_tests())
