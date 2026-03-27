<template>
  <div class="app">
    <div class="card">
      <h2>自动化深度研究智能体</h2>

      <input v-model="topic" placeholder="输入研究主题" @keyup.enter="go" />
      <div class="btn-row">
        <button @click="go" class="primary">开始研究</button>
        <button @click="openHistory" class="secondary">历史记录</button>
      </div>
    </div>

    <!-- 历史记录弹窗 -->
    <div v-if="showHistory" class="history-modal" @click.self="showHistory = false">
      <div class="history-box">
        <div class="history-header">
          <h3>历史研究</h3>
          <button @click="showHistory = false">×</button>
        </div>
        <div class="history-list">
          <div
            v-for="item in historyList"
            :key="item.session_id"
            class="history-item"
            @click="viewHistoryReport(item)"
          >
            <div class="topic">{{ item.topic }}</div>
            <div class="time">{{ item.created_at }}</div>
          </div>
          <div v-if="historyList.length === 0" class="empty">暂无历史记录</div>
        </div>
      </div>
    </div>

    <ResearchModal />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import ResearchModal from "./components/ResearchModal.vue";
import { useResearch } from "./composables/useResearch";

const topic = ref("");
const { startResearch, historyList, showHistory, fetchHistory, viewHistoryReport } = useResearch();

const go = () => {
  if (!topic.value) return;
  startResearch(topic.value);
};

const openHistory = async () => {
  await fetchHistory();
  showHistory.value = true;
};

onMounted(() => {
  fetchHistory();
});
</script>

<style scoped>
.app {
  min-height: 100vh;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.card {
  width: 100%;
  max-width: 650px;
  background: #fff;
  padding: 40px;
  border-radius: 16px;
  box-shadow: 0 4px 20px #0000000a;
}
input {
  width: 100%;
  padding: 14px 16px;
  margin: 20px 0;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  box-sizing: border-box;
}
.btn-row {
  display: flex;
  gap: 12px;
}
.primary {
  flex: 1;
  padding: 14px;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
}
.secondary {
  padding: 14px 20px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}

/* 历史弹窗 */
.history-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}
.history-box {
  width: 90%;
  max-width: 600px;
  max-height: 70vh;
  background: white;
  border-radius: 12px;
  overflow: hidden;
}
.history-header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.history-header button {
  font-size: 20px;
  border: none;
  background: none;
  cursor: pointer;
}
.history-list {
  padding: 16px 20px;
  overflow-y: auto;
  max-height: 50vh;
}
.history-item {
  padding: 12px;
  border-bottom: 1px solid #f1f1f1;
  cursor: pointer;
  border-radius: 6px;
}
.history-item:hover {
  background: #f8fafc;
}
.topic {
  font-weight: 500;
  margin-bottom: 4px;
}
.time {
  font-size: 12px;
  color: #999;
}
.empty {
  text-align: center;
  padding: 40px 0;
  color: #999;
}
</style>
