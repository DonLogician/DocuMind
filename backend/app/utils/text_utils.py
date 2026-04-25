import logging
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)


def split_text_into_chunks(
    text: str, chunk_size: int = 1000, chunk_overlap: int = 200
) -> List[str]:
    """
    使用 RecursiveCharacterTextSplitter 将长文本切分为块。
    优先按照段落、句子进行切分，保持语义的连贯性。
    """
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        logger.info(f"文本切分完成：总长度 {len(text)} 字符，切分为 {len(chunks)} 块。")
        return chunks
    except Exception as e:
        logger.error(f"文本切分失败: {str(e)}")
        raise e
