"""API路由"""
import asyncio
import uuid
from datetime import datetime
from typing import Dict
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import json

from app.models.schemas import ResearchRequest, ResearchResponse, ResearchStatus, TaskInfo
from app.core.state import create_initial_state
from app.core.graph import get_research_graph
from app.config import settings
from app.utils.logger import get_logger

router = APIRouter(prefix="/research", tags=["research"])
logger = get_logger(__name__)

# 会话存储（生产环境使用Redis）
sessions: Dict[str, dict] = {}


async def run_research_task(session_id: str, request: ResearchRequest):
    """异步运行研究任务"""

    try:
        # 获取会话
        session = sessions.get(session_id)
        if not session:
            return

        # 更新状态为 running
        session["status"] = "running"
        session["percentage"] = 0
        session["text"] = "正在启动研究任务..."
        session["current_action"] = "Starting research..."
        
        # 创建初始状态
        initial_state = create_initial_state(
            session_id=session_id,
            topic=request.topic,
            depth=request.depth
        )
        
        # 获取图并执行
        graph = get_research_graph()
        
        # 执行工作流
        result = await graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": session_id}}
        )
        
        # 更新会话
        session["status"] = "completed" if result["stage"] == "completed" else "failed"
        session["percentage"] = 100
        session["text"] = "研究任务已完成" if result["stage"] == "completed" else "研究任务失败"
        session["progress"] = 100
        session["result"] = {
            "report": result.get("final_report"),
            "sources": result.get("sources"),
            "findings": result.get("findings"),
            "cost": result.get("cost_tracker", {}).get("estimated_cost", 0)
        }
        session["updated_at"] = datetime.now().isoformat()
        
        if result.get("error_messages"):
            session["error_message"] = "; ".join(result["error_messages"])
        
        logger.info(
            "Research task completed",
            session_id=session_id,
            status=session["status"],
            sources_count=len(result.get("sources", []))
        )
        
    except Exception as e:
        logger.error("Research task failed", session_id=session_id, error=str(e))
        if session_id in sessions:
            sessions[session_id]["status"] = "failed"
            sessions[session_id]["error_message"] = str(e)


@router.post("/start", response_model=ResearchResponse)
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks
):
    """
    启动新的研究任务
    
    Args:
        request: 研究请求
        
    Returns:
        会话信息和状态
    """
    session_id = str(uuid.uuid4())
    
    # 初始化会话
    sessions[session_id] = {
        "session_id": session_id,
        "topic": request.topic,
        "depth": request.depth,
        "category": request.category,
        "status": "pending",
        "percentage": 0,
        "progress": 0,
        "text": "等待处理...",
        "stage": "pending",
        "current_action": "Initializing...",
        "tasks": [],
        "result": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    # 启动异步任务
    asyncio.create_task(run_research_task(session_id, request))

    logger.info(
        "Research task started",
        session_id=session_id,
        topic=request.topic,
        depth=request.depth
    )

    return ResearchResponse(
        session_id=session_id,
        status="running",
        message="研究已开始"
    )


@router.get("/{session_id}/status", response_model=ResearchStatus)
async def get_research_status(session_id: str):
    """
    获取研究任务状态

    Args:
        session_id: 会话ID

    Returns:
        当前研究状态和进度
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = sessions[session_id]
    result = session.get("result", {})

    # 构建任务列表
    tasks = session.get("tasks", [])

    return ResearchStatus(
        session_id=session_id,
        status=session["status"],
        percentage=session.get("percentage", 0),
        text=session.get("text", ""),
        tasks=tasks,
        report=result.get("report"),
        sources=result.get("sources"),
        findings=result.get("findings"),
        cost_estimate=result.get("cost"),
        error_message=session.get("error_message"),
        created_at=session.get("created_at"),
        updated_at=session.get("updated_at")
    )


@router.get("/{session_id}/stream")
async def stream_research_progress(session_id: str):
    """
    流式获取研究进度（Server-Sent Events）

    推送类型:
    - progress: 进度更新
    - plan: 研究计划
    - task_summary: 任务摘要
    - report: 报告生成
    - completed: 任务完成
    - error: 错误信息

    Args:
        session_id: 会话ID

    Returns:
        SSE事件流
    """
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    async def event_generator():
        last_status = None

        while True:
            if session_id not in sessions:
                yield f"data: {json.dumps({'type': 'error', 'message': 'Session not found'})}\n\n"
                break

            session = sessions[session_id]

            # 构建状态更新
            current_status = {
                "type": "progress",
                "session_id": session_id,
                "status": session["status"],
                "percentage": session.get("percentage", 0),
                "text": session.get("text", ""),
                "tasks": session.get("tasks", [])
            }

            # 只在状态变化时发送
            if current_status != last_status:
                yield f"data: {json.dumps(current_status)}\n\n"
                last_status = current_status.copy()

            # 任务完成或失败时退出
            if session["status"] in ["completed", "failed"]:
                result = session.get("result", {})

                if session["status"] == "completed":
                    # 发送完成类型
                    final_data = {
                        "type": "completed",
                        "session_id": session_id,
                        "status": "completed",
                        "percentage": 100,
                        "report": result.get("report"),
                        "sources": result.get("sources"),
                        "findings": result.get("findings"),
                        "cost_estimate": result.get("cost")
                    }
                else:
                    # 发送错误类型
                    final_data = {
                        "type": "error",
                        "session_id": session_id,
                        "status": "failed",
                        "error_message": session.get("error_message", "任务执行失败")
                    }

                yield f"data: {json.dumps(final_data)}\n\n"
                break

            await asyncio.sleep(1)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.get("/list")
async def list_sessions():
    """列出所有会话（用于调试）"""
    return {
        "list": [
            {
                "session_id": sid,
                "topic": s["topic"][:50] + "..." if len(s["topic"]) > 50 else s["topic"],
                "status": s["status"],
                "percentage": s.get("percentage", 0),
                "created_at": s.get("created_at")
            }
            for sid, s in sessions.items()
        ]
    }
