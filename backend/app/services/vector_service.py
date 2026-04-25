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
            # 临时关闭 SSL 校验或使用无校验本地请求，防止国内因证书拦截报错
            import urllib3

            urllib3.disable_warnings()
            os.environ["CURL_CA_BUNDLE"] = ""
            os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
            os.environ["HF_HUB_DISABLE_SSL_VERIFY"] = "1"

            # 清除死代理设置
            for k in ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"]:
                if k in os.environ:
                    del os.environ[k]

            os.environ["HF_HUB_OFFLINE"] = "1"
            # 禁用所有代理，防止 Python 从 Windows 注册表读取了已关闭的代理
            os.environ["NO_PROXY"] = "*"
            os.environ["no_proxy"] = "*"

            # 配置 BGE 嵌入模型（专门对中文进行了优化）
            # 由于运行在开发机器上，默认先使用 CPU (如有 GPU 可改为 'cuda')
            model_name = settings.EMBEDDING_MODEL
            model_kwargs = {"device": "cpu"}  # 显存不足或未配置时，默认改用 cpu
            encode_kwargs = {
                "normalize_embeddings": True
            }  # BGE 模型推荐 cosine 相似度需 normalize

            # 如果本地已经下载，我们可以尝试加上 local_files_only 避免它一直请求网络
            # 另外为了防止 proxy 的问题，我们用缓存直接读取
            try:
                self.embeddings = HuggingFaceBgeEmbeddings(
                    model_name=model_name,
                    model_kwargs={**model_kwargs, "local_files_only": True},
                    encode_kwargs=encode_kwargs,
                )
            except Exception as e:
                logger.warning(
                    f"使用 local_files_only=True 加载失败: {str(e)}，尝试普通加载..."
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
        if self.vector_store is None:
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

    async def similarity_search(
        self,
        query: str,
        k: int = 4,
        doc_id: str = None,
        use_mmr: bool = True,
        fetch_k: int = 15,
    ) -> List[Document]:
        """
        基于用户 query 请求执行语义相似度检索，返回最相关的 k 个文档片段。
        包含检索过滤与 MMR（最大边际相关性）排序优化，确保结果既相关又具备多样性。
        """
        if self.vector_store is None:
            raise ValueError("向量数据库未正常初始化，无法执行检索。")

        try:
            # 检索结果过滤机制：如果指定了 doc_id，则只在对应文档内检索
            filter_dict = {"doc_id": doc_id} if doc_id else None

            if use_mmr:
                # 使用最大边际相关性(MMR)进行优化，避免给出的文档块内容高度重复
                results = self.vector_store.max_marginal_relevance_search(
                    query, k=k, fetch_k=fetch_k, filter=filter_dict
                )
            else:
                # 基础的余弦相似度检索
                results = self.vector_store.similarity_search(
                    query, k=k, filter=filter_dict
                )
            return results
        except Exception as e:
            logger.error(f"向量检索过程异常: {str(e)}")
            raise e

    def get_retriever(self, k: int = 4, doc_id: str = None):
        """
        供 LangChain 问答链直接调用的基础 Retriever 实例
        """
        filter_dict = {"doc_id": doc_id} if doc_id else None
        return self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={"k": k, "fetch_k": 15, "filter": filter_dict},
        )

    async def delete_document(self, doc_id: str) -> bool:
        """
        根据 doc_id 从向量数据库中删除对应的所有文档块
        """
        if self.vector_store is None:
            return False
        try:
            # 查找匹配 doc_id 的条目并删除
            # current Chroma db returns objects using .get
            result = self.vector_store.get(where={"doc_id": doc_id})
            if result and result.get("ids"):
                self.vector_store.delete(ids=result["ids"])
                logger.info(f"已从 ChromaDB 中删除文档 {doc_id} 的全部块。")
                return True
            return False
        except Exception as e:
            logger.error(f"删除向量文档时发生异常: {str(e)}")
            return False


# 导出单例实例化对象，以便全工程共享连接池资源
vector_service = VectorService()
