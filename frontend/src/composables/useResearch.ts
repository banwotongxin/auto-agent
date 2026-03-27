//通过SSE与后端通信并处理流式数据
import { onUnmounted, ref } from "vue";
import { marked } from "marked";
import type {
  SSEData,
  StartResearchResponse,
  TodoItem,
  ResearchHistory,
  ResearchStatus,
} from "@/types/research";

function createResearchStore() {
  const isOpen = ref(false); //控制研究弹窗
  const isLoading = ref(false); //控制加载状态
  const researchTopic = ref(""); //保存用户的研究主题
  const progressText = ref("准备开始..."); //显示实时状态
  const progressPercentage = ref(0); //显示进度条
  const taskList = ref<TodoItem[]>([]); //保存AI 拆分的研究任务列表
  const reportContent = ref(""); //保存最终 Markdown 报告全文
  const errorMsg = ref(""); //捕获并存储错误信息
  const currentSessionId = ref<string | null>(null); //存储会话ID

  // 历史记录
  const historyList = ref<ResearchHistory[]>([]);
  const showHistory = ref(false);

  // 轮询定时器（用于主动获取任务状态）
  let statusTimer: number | null = null;

  // 获取研究任务状态
  const fetchResearchStatus = async (session_id: string) => {
    try {
      const res = await fetch(`/research/${session_id}/status`);
      const data = (await res.json()) as ResearchStatus;

      // 同步到页面
      progressPercentage.value = data.percentage;
      progressText.value = data.text;
      taskList.value = data.tasks || [];
      researchTopic.value = data.topic;

      if (data.report) {
        reportContent.value = data.report;
      }

      // 研究完成则停止轮询
      if (data.status === "completed" || data.status === "failed") {
        stopStatusPoll();
        isLoading.value = false;
      }

      return data;
    } catch (err) {
      console.error("获取状态失败", err);
      return null;
    }
  };

  // 自动轮询状态（2秒一次）
  const startStatusPoll = (session_id: string) => {
    stopStatusPoll();
    fetchResearchStatus(session_id);
    statusTimer = window.setInterval(() => {
      fetchResearchStatus(session_id);
    }, 2000);
  };

  // 停止轮询
  const stopStatusPoll = () => {
    if (statusTimer) {
      clearInterval(statusTimer);
      statusTimer = null;
    }
  };

  // 获取历史记录
  const fetchHistory = async () => {
    try {
      const res = await fetch("/research/list");
      const data = await res.json();
      historyList.value = data.list || [];
    } catch (err) {
      console.error("获取历史记录失败", err);
    }
  };

  // 查看历史报告
  const viewHistoryReport = async (item: ResearchHistory) => {
    researchTopic.value = item.topic;
    reportContent.value = item.report || "";
    progressText.value = "✅ 历史报告";
    progressPercentage.value = 100;
    isLoading.value = false;
    errorMsg.value = "";
    isOpen.value = true;
    showHistory.value = false;
    
    //加载任务状态
    if (item.session_id) {
      await fetchResearchStatus(item.session_id);
    }
  };

  //重置
  const resetState = () => {
    stopStatusPoll()
    progressPercentage.value = 0;
    progressText.value = "连接中...";
    taskList.value = [];
    reportContent.value = "";
    errorMsg.value = "";
    currentSessionId.value = null;
  };

  const startResearch = async (topic: string) => {
    researchTopic.value = topic;
    isOpen.value = true;
    isLoading.value = true;
    resetState();

    try {
      //step1:启动研究，获取session_id
      const startRes = await fetch("/research/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ topic }),
      });

      if (!startRes.ok) {
        throw new Error(`启动研究失败：${startRes.statusText}`);
      }

      const startData: StartResearchResponse = await startRes.json();
      currentSessionId.value = startData.session_id;

      //启动状态轮询
      startStatusPoll(startData.session_id)
    

      //step2:用 session_id建立 SSE 连接
      //SSE连接:new EventSource(...)官方内置的 SSE 连接对象;
      //${encodeURIComponent(topic)}把中文 / 特殊字符转成安全的网址格式
      const es = new EventSource(`/research/${startData.session_id}/stream`);

      es.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data) as SSEData;
          handleSSE(data);
        } catch (err) {
          console.error("SSE数据解析失败", err);
        }
      };

      es.onerror = (err) => {
        console.error("SSE连接错误", err);
        errorMsg.value = "连接断开，请重试";
        isLoading.value = false;
        es.close();
      };

      // 研究完成或出错时自动关闭连接
      es.addEventListener("close", () => {
        es.close();
      });
    } catch (err) {
      errorMsg.value = err instanceof Error ? err.message : "启动研究失败";
      isLoading.value = false;
    }
  };

  //处理 SSE 数据
  const handleSSE = (data: SSEData) => {
    switch (data.type) {
      case "progress":
        progressText.value = data.text || "处理中...";
        if (data.percentage !== undefined) {
          progressPercentage.value = data.percentage;
        }
        break;

      case "plan":
        taskList.value = data.data || [];
        progressText.value = data.text || "已生成研究计划";
        break;

      case "task_summary":
        progressText.value = data.summary || "任务完成";
        if (data.percentage) progressPercentage.value = data.percentage;
        break;

      case "report":
        reportContent.value = data.data || "";
        progressText.value = "正在生成最终报告";
        break;

      case "completed":
        progressPercentage.value = 100;
        progressText.value = "✅ 研究全部完成";
        isLoading.value = false;
        stopStatusPoll()
        fetchHistory()
        //自动关闭 SSE 连接
        if (currentSessionId.value) {
          const es = new EventSource(`/research/${currentSessionId.value}/stream`);
          es.close();
          currentSessionId.value = null;
        }
        break;

      case "error":
        errorMsg.value = data.message || "研究出错";
        isLoading.value = false;
        stopStatusPoll()
        break;
    }
  };

  //关闭弹窗
  const closeModal = () => {
    isOpen.value = false;
    //关闭弹窗时断开SSE连接
    if (currentSessionId.value) {
      const es = new EventSource(`/research/${currentSessionId.value}/stream`);
      es.close();
      currentSessionId.value = null;
    }
    stopStatusPoll()
  };

  // 页面销毁时停止定时器
  onUnmounted(() => stopStatusPoll())
  
  //渲染Markdown
  const renderedReport = () => marked.parse(reportContent.value, { gfm: true, breaks: true });

  return {
    isOpen,
    isLoading,
    researchTopic,
    progressText,
    progressPercentage,
    taskList,
    reportContent,
    errorMsg,
    startResearch,
    closeModal,
    renderedReport,
    historyList,
    showHistory,
    fetchHistory,
    viewHistoryReport,
  };
}

let researchStore: ReturnType<typeof createResearchStore> | null = null;

export function useResearch() {
  if (!researchStore) {
    researchStore = createResearchStore();
  }
  return researchStore;
}
