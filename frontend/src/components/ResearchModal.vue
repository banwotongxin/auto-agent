<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal">
      <div class="header">
        <h3>深度研究：{{ researchTopic }}</h3>
        <button @click="closeModal" class="close">×</button>
      </div>

      <!-- 进度条 -->
      <div class="progress">
        <div class="bar">
          <div class="fill" :style="{ width: progressPercentage + '%' }"></div>
        </div>
        <p>{{ progressText }}</p>
      </div>

      <!-- 任务列表（带状态） -->
      <div v-if="taskList.length > 0" class="task-section">
        <h4>📋 研究任务</h4>
        <div class="task-list">
          <div v-for="task in taskList" :key="task.id" class="task-item">
            <span class="task-index">{{ task.id }}</span>
            <span class="task-title">{{ task.title }}</span>
            <span class="task-status" :class="task.status">
              {{
                task.status === "pending"
                  ? "等待中"
                  : task.status === "running"
                    ? "执行中"
                    : task.status === "completed"
                      ? "已完成"
                      : "失败"
              }}
            </span>
          </div>
        </div>
      </div>

      <!-- 内容区 -->
      <div class="body">
        <div v-if="isLoading" class="loading">
          <div class="spinner"></div>
        </div>
        <div v-else-if="errorMsg" class="error">{{ errorMsg }}</div>
        <div v-else class="report" v-html="renderedReport"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useResearch } from "../composables/useResearch";
const {
  isOpen,
  researchTopic,
  progressText,
  progressPercentage,
  isLoading,
  errorMsg,
  taskList,
  renderedReport,
  closeModal,
} = useResearch();
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.modal {
  width: 94vw;
  height: 90vh;
  background: #fff;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.header {
  padding: 16px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.close {
  font-size: 24px;
  border: none;
  background: none;
  cursor: pointer;
}

/* 进度条 */
.progress {
  padding: 12px 20px;
  border-bottom: 1px solid #eee;
}
.bar {
  height: 8px;
  background: #f1f1f1;
  border-radius: 4px;
  overflow: hidden;
}
.fill {
  height: 100%;
  background: #4f46e5;
  transition: width 0.3s;
}

/* 任务列表 */
.task-section {
  padding: 12px 20px;
  border-bottom: 1px solid #eee;
}
.task-section h4 {
  margin: 0 0 10px;
  font-size: 14px;
  color: #4f46e5;
}
.task-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 180px;
  overflow-y: auto;
}
.task-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 14px;
}
.task-index {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #4f46e5;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
}
.task-title {
  flex: 1;
}
.task-status {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
}
.task-status.pending {
  background: #f3f4f6;
  color: #6b7280;
}
.task-status.running {
  background: #dbeafe;
  color: #3b82f6;
}
.task-status.completed {
  background: #d1fae5;
  color: #065f46;
}
.task-status.failed {
  background: #fee2e2;
  color: #991b1b;
}

.body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}
.loading {
  display: flex;
  justify-content: center;
  padding: 40px;
}
.spinner {
  width: 36px;
  height: 36px;
  border: 4px solid #f1f1f1;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
.error {
  color: #f43f5e;
  padding: 20px;
  text-align: center;
}
.report {
  line-height: 1.7;
  font-size: 15px;
}
</style>
