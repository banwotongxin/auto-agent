#!/usr/bin/env python3
"""
AutoResearch Agent 使用示例

此脚本演示如何直接使用研究工作流，不通过API服务。
"""
import asyncio
import uuid
from app.core.state import create_initial_state
from app.core.graph import get_research_graph
from app.utils.logger import setup_logging


async def run_research_example():
    """运行研究示例"""
    
    # 设置日志
    setup_logging(debug=True)
    
    # 研究主题
    topic = "人工智能在气候变化预测中的应用"
    depth = "quick"  # 可选: quick, standard, deep
    
    print(f"\n{'='*60}")
    print(f"开始研究: {topic}")
    print(f"研究深度: {depth}")
    print(f"{'='*60}\n")
    
    # 创建初始状态
    session_id = str(uuid.uuid4())
    initial_state = create_initial_state(
        session_id=session_id,
        topic=topic,
        depth=depth
    )
    
    # 获取研究工作流
    graph = get_research_graph()
    
    try:
        # 执行研究工作流
        result = await graph.ainvoke(
            initial_state,
            config={"configurable": {"thread_id": session_id}}
        )
        
        # 输出结果
        print(f"\n{'='*60}")
        print("研究完成!")
        print(f"{'='*60}\n")
        
        print(f"最终状态: {result['stage']}")
        print(f"收集来源: {len(result.get('sources', []))} 个")
        print(f"关键发现: {len(result.get('findings', []))} 个")
        
        cost_tracker = result.get('cost_tracker', {})
        print(f"LLM调用: {cost_tracker.get('llm_calls', 0)} 次")
        print(f"搜索调用: {cost_tracker.get('search_calls', 0)} 次")
        
        # 输出报告预览
        report = result.get('final_report', '')
        if report:
            print(f"\n{'='*60}")
            print("研究报告预览 (前1000字符):")
            print(f"{'='*60}\n")
            print(report[:1000])
            print("\n... (报告已截断)")
        
        # 保存报告到文件
        if report:
            filename = f"research_report_{session_id[:8]}.md"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"\n报告已保存到: {filename}")
        
    except Exception as e:
        print(f"\n研究过程中出错: {e}")
        raise


if __name__ == "__main__":
    # 运行示例
    print("""
╔══════════════════════════════════════════════════════════╗
║       AutoResearch Agent 示例脚本                         ║
║       直接使用研究工作流进行深度研究                       ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # 检查环境变量
    import os
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️ 警告: 未配置 LLM API 密钥")
        print("请设置 ANTHROPIC_API_KEY 或 OPENAI_API_KEY 环境变量")
        print("\n示例:")
        print("  Windows: set ANTHROPIC_API_KEY=your_key")
        print("  Linux/Mac: export ANTHROPIC_API_KEY=your_key")
        sys.exit(1)
    
    if not os.getenv("TAVILY_API_KEY"):
        print("\n⚠️ 警告: 未配置 TAVILY_API_KEY 环境变量")
        print("搜索功能可能无法正常工作")
    
    asyncio.run(run_research_example())
