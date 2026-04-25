from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api import upload, chat

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="DocuMind - 智能文档研讨助手后端 API",
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 实际部署时应限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", summary="健康检查")
async def health_check():
    return {
        "code": 200,
        "message": "success",
        "data": {"status": "ok"},
    }


@app.get("/api/version", summary="获取版本信息")
async def get_version():
    return {
        "code": 200,
        "message": "success",
        "data": {"name": settings.APP_NAME, "version": settings.APP_VERSION},
    }


# 注册文档上传路由
app.include_router(upload.router)

# 注册对话路由
app.include_router(chat.router)
