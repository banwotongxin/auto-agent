//类型定义

//研究任务：深度研究智能体把一个大问题拆成很多小任务，每个小任务就是一个 TodoItem
export interface TodoItem {
  id: number;
  title: string;
  intent: string;
  query: string;
  status: "pending" | "running" | "completed" | "failed";
}

// 后端 SSE 推送的所有消息格式： 智能体实时发给前端的进度 / 状态 / 报告
export interface SSEData {
  //progress研究进度更新；plan智能体拆分出研究计划；task_summary单个任务执行总结
  //report最终研究报告；error研究出错；completed全部研究完成
  type: "progress" | "plan" | "task_summary" | "report" | "error" | "completed";
  percentage?: number;
  text?: string;
  data?: String | any;
  task_id?: number;
  summary?: string;
  message?: string;
  report?: string;
  sources?: any[];
  findings?: any[];
  cost_estimate?: number;
}

//启动研究接口的响应结构
export interface StartResearchResponse {
  session_id: string;
  status: string;
  message?: string;
}

// 历史研究记录
export interface ResearchHistory {
  session_id: string;
  topic: string;
  status: string;
  created_at: string;
  report?: string;
}

export interface ResearchStatus {
  session_id: string;
  topic: string;
  status: "running" | "completed" | "failed";
  percentage: number;
  text: string;
  tasks: TodoItem[];
  report?: string;
}
