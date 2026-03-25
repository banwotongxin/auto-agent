#!/usr/bin/env python3
"""
AutoResearch Agent 启动脚本
"""
import sys
import uvicorn
from app.config import settings


def main():
    """主函数"""
    print(f"""
╔══════════════════════════════════════════════════════════╗
║           AutoResearch Agent 自动化深度研究智能体         ║
║                      v{settings.APP_VERSION}                        ║
╚══════════════════════════════════════════════════════════╝

启动配置:
  - 主机: {settings.API_HOST}
  - 端口: {settings.API_PORT}
  - 调试模式: {settings.DEBUG}
  - LLM提供商: {settings.DEFAULT_LLM_PROVIDER}
  - 默认模型: {settings.DEFAULT_MODEL}

API文档: http://{settings.API_HOST}:{settings.API_PORT}/docs
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else settings.API_WORKERS,
        log_level="debug" if settings.DEBUG else "info"
    )


if __name__ == "__main__":
    main()
