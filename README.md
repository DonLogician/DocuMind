# DocuMind - 智能文档研讨助手

DocuMind 是一个基于大语言模型（LLM）的全栈智能文档研讨系统。它能够解析多种格式的文档（PDF、TXT、EPUB），并与用户进行有记忆、有深度的多轮对话，支持对文档内容的深入探讨、提取和引用分析。

## 项目进度

当前已完成 **Day 1** 的基础功能开发：
- [x] FastAPI 后端项目基础架构搭建
- [x] Conda (`documind`) 环境配置与依赖锁定
- [x] 多格式文档流式异步上传接口 (`/api/upload`)
- [x] 基于 `unstructured` 和 `ebooklib` 的文档解析器实现 (支持 PDF、EPUB、TXT)

## 技术栈

- **后端**: Python 3.10, FastAPI, Uvicorn, aiofiles
- **文档处理**: unstructured, ebooklib, BeautifulSoup4
- **AI 框架 (计划中)**: LangChain, Chroma (向量数据库), BAAI/bge-small-zh-v1.5 (Embedding), 通义千问 API (LLM)
- **前端 (计划中)**: Vue 3, Element Plus, Pinia

## 快速开始

### 1. 后端服务启动

确保你已经安装了 [Miniconda](https://docs.conda.io/en/latest/miniconda.html) 或 Anaconda。

```bash
cd backend

# 使用环境文件创建虚拟环境
conda env create -f environment.yml

# 激活环境
conda activate documind

# 复制一份环境变量文件并填入你的配置（如 TONGYI_API_KEY）
cp .env.example .env

# 启动 FastAPI 服务
uvicorn app.main:app --reload
```

服务启动后，可以通过访问 `http://127.0.0.1:8000/docs` 查看自动生成的交互式 API 文档。
