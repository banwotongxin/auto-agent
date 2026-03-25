"""WebSocket路由"""
import json
from typing import Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.utils.logger import get_logger

router = APIRouter(prefix="/research", tags=["websocket"])
logger = get_logger(__name__)


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # session_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, session_id: str, websocket: WebSocket):
        """建立连接"""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"WebSocket connected: {session_id}")
    
    def disconnect(self, session_id: str):
        """断开连接"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_message(self, session_id: str, message: dict):
        """发送消息"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_json(message)
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
    
    async def broadcast(self, message: dict):
        """广播消息"""
        disconnected = []
        for session_id, connection in self.active_connections.items():
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(session_id)
        
        # 清理断开的连接
        for session_id in disconnected:
            self.disconnect(session_id)


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/{session_id}")
async def research_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket实时通信
    
    客户端可以发送以下命令：
    - {"action": "get_status"}: 获取当前状态
    - {"action": "ping"}: 心跳检测
    
    服务端会主动推送：
    - 研究进度更新
    - 状态变化通知
    - 最终结果
    """
    await manager.connect(session_id, websocket)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                action = message.get("action")
                
                if action == "ping":
                    await manager.send_message(session_id, {"type": "pong"})
                    
                elif action == "get_status":
                    # 从路由模块获取会话信息
                    from app.api.routes import sessions
                    if session_id in sessions:
                        await manager.send_message(session_id, {
                            "type": "status",
                            "data": sessions[session_id]
                        })
                    else:
                        await manager.send_message(session_id, {
                            "type": "error",
                            "message": "Session not found"
                        })
                else:
                    await manager.send_message(session_id, {
                        "type": "error",
                        "message": f"Unknown action: {action}"
                    })
                    
            except json.JSONDecodeError:
                await manager.send_message(session_id, {
                    "type": "error",
                    "message": "Invalid JSON"
                })
                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)


# 导出管理器供其他模块使用
__all__ = ["router", "manager"]
