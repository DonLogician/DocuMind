import os
import logging
from typing import List, Dict, Any

from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from app.config import settings

logger = logging.getLogger(__name__)


class VectorService:
    def __init__(self):
        try:
            # 配置 BGE 嵌入模型（专门对中文进行了优化）
            # 由于运行在开发机器上，默认先使用 CPU (如有 GPU 可改为 'cuda')
            model_name = settings.EMBEDDING_MODEL
            model_kwargs = {"device": "cpu"}
            encode_kwargs = {
                "normalize_embeddings": True
            }  # BGE 模型推荐 cosine 相似度需 normalize

            logger.info(
                f"正在加载 Embedding 模型: {model_name}，这可能需要一点时间下载..."
            )

            self.embeddings = HuggingFaceBgeEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                encode_kwargs=encode_kwargs,
            )

            # 确保 Chroma DB 持久化目录存在
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)

            # 初始化 Chroma 客户端
            self.vector_store = Chroma(
                collection_name="documind_collection",
                embedding_function=self.embeddings,
                persist_directory=settings.CHROMA_PERSIST_DIR,
            )

            logger.info("Chroma 向量引擎与 BGE 模型初始化成功！")
        except Exception as e:
            logger.error(f"初始化向量服务失败: {str(e)}")
            self.embeddings = None
            self.vector_store = None

    async def add_documents(self, chunks: List[str], metadata: Dict[str, Any]) -> None:
        """
        异步地将文本分片转换为向量并入库
        """
        if not self.vector_store:
            raise ValueError("向量数据库未正常初始化，无法添加文档。")

        try:
            documents = []
            for i, chunk in enumerate(chunks):
                # 深拷贝 metadata，为每一个块附加独有的编号位置信息
                chunk_meta = metadata.copy()
                chunk_meta["chunk_index"] = i
                documents.append(Document(page_content=chunk, metadata=chunk_meta))

            # 执行将文本写入向量数据库
            self.vector_store.add_documents(documents)

            # Langchain-Chroma 新版虽然在进程关闭前大多自动持久化，但我们安全起见：
            self.vector_store.persist()
            logger.info(
                f"入库成功：文档 {metadata.get('doc_id')} （共 {len(documents)} 块）已持久化至 ChromaDB。"
            )

        except Exception as e:
            logger.error(f"添加向量文档失败: {str(e)}")
            raise e

    async def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """
        基于用户 query 请求执行语义相似度检索，返回最相关的 k 个文档片段
        """
        if not self.vector_store:
            raise ValueError("向量数据库未正常初始化，无法执行检索。")

        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"向量检索过程异常: {str(e)}")
            raise e


# 导出单例实例化对象，以便全工程共享连接池资源
vector_service = VectorService()
