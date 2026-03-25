"""日志配置"""
import sys
import structlog
from pythonjsonlogger import jsonlogger
import logging


def setup_logging(debug: bool = False):
    """设置日志配置"""
    
    # 配置标准库日志
    log_level = logging.DEBUG if debug else logging.INFO
    
    # 创建处理器
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    
    # 使用JSON格式
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    handler.setFormatter(formatter)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]
    
    # 配置structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str):
    """获取日志记录器"""
    return structlog.get_logger(name)
