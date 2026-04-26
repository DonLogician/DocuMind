# DocuMind - 智能文档研讨助手

DocuMind 是一个基于大语言模型（LLM）的全栈智能文档研讨系统。它能够解析多种格式的文档（PDF、TXT、EPUB），并与用户进行有记忆、有深度的多轮对话，支持对文档内容的深入探讨、提取和引用分析。

## 项目进度

当前已完成 **Day 1 到 Day 3** 的基础与核心功能开发：
- [x] FastAPI 后端项目基础架构搭建
- [x] Conda (`documind`) 环境配置与依赖锁定
- [x] 多格式文档流式异步上传接口 (`/api/upload`)
- [x] 基于 `unstructured` 和 `ebooklib` 的文档解析器实现 (支持 PDF、EPUB、TXT)
- [x] **Day 2**: LangChain `RecursiveCharacterTextSplitter` 文本分块实现
- [x] **Day 2**: 引入 Chroma 向量引擎本地持久化方案
- [x] **Day 2**: 集成 HuggingFace 离线 `BAAI/bge-small-zh-v1.5` 中文词嵌入模型
- [x] **Day 2**: 构建 `VectorService` 核心，支持文档入库、根据文档 ID 删除、MMR 边际相关语义检索聚合
- [x] **Day 3**: 对话记忆系统实现 (`ConversationSummaryBufferMemory`) 用于长篇上下文化的总结
- [x] **Day 3**: 深度整合 `RetrievalQA` 检索链与聊天端点，处理对话历史管理机制
- [x] **Day 3**: 依赖包隔离升级与系统稳定性修复 (LangChain 环境对齐 v0.2.16)

目前的测试脚本及验证入口：
- 存放于 `backend/tests/` 目录下 (`test_upload.py`, `test_day2.py` 和 `test_day3.py`)

## 技术栈

- **后端**: Python 3.10, FastAPI, Uvicorn, aiofiles
- **文档处理**: unstructured, ebooklib, BeautifulSoup4
- **AI 框架**: LangChain, Chroma (向量引擎), BAAI/bge-small-zh-v1.5 (Embedding 离线加载), 通义千问 API (LLM)
- **前端 (设计与框架搭建中)**: Vue 3, Element Plus, Pinia

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
