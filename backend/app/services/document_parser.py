import os
import logging
from typing import Optional
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from unstructured.partition.pdf import partition_pdf
from unstructured.partition.text import partition_text

logger = logging.getLogger(__name__)
# 确保控制台能输出 logger 警告
logging.basicConfig(level=logging.INFO)


async def parse_document(file_path: str, extension: str) -> str:
    """
    根据文件扩展名路由到相应的解析器，并提取纯文本内容
    """
    try:
        if extension == ".pdf":
            logger.info(f"正在使用 unstructured 解析 PDF: {file_path}")
            # partition_pdf 内部使用 pdfminer 等提取文本和结构
            elements = partition_pdf(filename=file_path)
            return "\n\n".join([str(el) for el in elements if str(el).strip()])

        elif extension == ".txt":
            logger.info(f"正在使用 unstructured 解析 TXT: {file_path}")
            elements = partition_text(filename=file_path)
            return "\n\n".join([str(el) for el in elements if str(el).strip()])

        elif extension == ".epub":
            logger.info(f"正在使用 ebooklib 解析 EPUB: {file_path}")
            return parse_epub(file_path)

        else:
            raise ValueError(f"不受支持的文档扩展名: {extension}")

    except Exception as e:
        logger.error(f"解析文档 {file_path} 时发生错误: {str(e)}")
        raise e


def parse_epub(file_path: str) -> str:
    """
    使用 ebooklib 提取 epub 文档的纯本文
    由于提取出的是 HTML 内容，使用 BeautifulSoup 清洗 HTML 标签
    """
    try:
        book = epub.read_epub(file_path)
        chapters = []
        for item in book.get_items():
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                # 使用 bs4 剥离 HTML 标签获取纯文本
                soup = BeautifulSoup(item.get_body_content(), "html.parser")
                text = soup.get_text(separator="\n", strip=True)
                if text:
                    chapters.append(text)
        return "\n\n".join(chapters)
    except Exception as e:
        logger.error(f"EPUB 结构读取失败: {str(e)}")
        raise e
