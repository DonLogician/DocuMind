# DocuMind - 智能文档研讨助手

DocuMind 是一个基于大语言模型（LLM）的全栈智能文档研讨系统。它能够解析多种格式的文档（PDF、TXT、EPUB），并与用户进行有记忆、有深度的多轮对话，支持对文档内容的深入探讨、提取和引用分析。

## 技术栈

- **后端**: Python 3.10, FastAPI, Uvicorn, aiofiles
- **文档处理**: unstructured, ebooklib, BeautifulSoup4
- **AI 框架**: LangChain, Chroma (向量引擎), BAAI/bge-small-zh-v1.5 (Embedding 离线加载), 通义千问 API (LLM)
- **前端**: Vue 3, Element Plus, Vite, Vue Router

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
