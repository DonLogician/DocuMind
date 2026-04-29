# DocuMind - 智能文档研讨助手

DocuMind 是一个基于大语言模型（LLM）的全栈智能文档研讨系统。它能够解析多种格式的文档（PDF、TXT、EPUB），并与用户进行有记忆、有深度的多轮对话，支持对文档内容的深入探讨、提取和引用分析。

## 技术栈

- **后端**: Python 3.10, FastAPI, Uvicorn, aiofiles
- **文档处理**: unstructured, ebooklib, BeautifulSoup4
- **AI 框架**: LangChain, Chroma (向量引擎), BAAI/bge-small-zh-v1.5 (Embedding 离线加载), 通义千问 API (LLM)
- **前端**: Vue 3, Element Plus, Vite, Vue Router

## 项目功能

1. **多格式私有知识库构建**：原生支持 PDF、TXT、EPUB 等常见文档格式上传。结合 LangChain 文本分块特性与 Chroma 离线向量引擎，快速实现私有 RAG（检索增强生成）数据地基。
2. **重度研讨型 ReAct Agent**：突破单次 RAG 局限，使用自主判断和工具使用的独立智能体。当面对复杂设问时，大模型能自动推演并在内部执行多次交叉检索比对，最终输出富有深度的事实答案。
3. **全局混层会话长记忆**：注入基于摘要拦截的上下文管线（Conversation Summary Buffer Memory）。即便面对数十轮的持续拷问也能确保记忆连贯不出戏，且永不崩溃与溢出 Token 上限。
4. **现代化智能聊天交互舱**：使用响应式且拥有 Markdown 原生解析的开箱即用对话流体验。支持历史会话无缝穿梭（本地存储集成）、双重对话引擎动态热切、以及精确制导的引用溯源边栏呈现。

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

### 2. 前端服务启动

确保你已经安装了 [Node.js](https://nodejs.org/)。

```bash
cd frontend

# 安装依赖
npm install

# 启动 Vite 开发服务器
npm run dev
```

服务启动后，在浏览器访问 `http://localhost:5173/` 即可使用文档管理和研讨对话界面。注意：前端通过 Vite 代理自动将 `/api` 请求转发至后端的 `8000` 端口，所以请确保后端正常运行。
