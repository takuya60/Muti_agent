<script setup lang="ts">
import { ref } from 'vue'

const message = ref('')
const chatHistory = ref([
  { role: 'system', content: '你好！根据你的画像分析，你的数学基础较弱，我们先从「逻辑回归」的基础概念开始吧。' },
  { role: 'user', content: 'Sigmoid 函数是做什么的？' },
  { role: 'system', content: '好问题！Sigmoid 函数可以理解为一个“压缩器”，它能把任何实数映射到 0 和 1 之间。在逻辑回归中，我们用它来输出概率值。' }
])

const sendMessage = () => {
  if (message.value.trim()) {
    chatHistory.value.push({ role: 'user', content: message.value })
    message.value = ''
    setTimeout(() => {
      chatHistory.value.push({ role: 'system', content: '系统正在基于知识图谱进行检索...' })
    }, 800)
  }
}
</script>

<template>
  <div class="learning-container">
    <!-- 顶部悬浮导航 -->
    <header class="glass-header">
      <div class="logo">Agent<span>Edu</span></div>
      <div class="status-center">
        <span class="label">当前目标：</span>
        <span class="value">逻辑回归</span>
        <el-divider direction="vertical" />
        <span class="label">进度：</span>
        <span class="value active-value">3/8 知识点</span>
      </div>
      <div class="user-profile">
        <el-avatar size="small" src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png" />
      </div>
    </header>

    <div class="main-layout">
      <!-- 左侧对话舱 -->
      <aside class="chat-panel glass-panel">
        <div class="panel-header">
          <h3>智能导师</h3>
          <div class="agent-status">
            <span class="dot pulse"></span>
            诊断 Agent 待命中
          </div>
        </div>
        
        <div class="chat-history">
          <div 
            v-for="(msg, index) in chatHistory" 
            :key="index"
            :class="['message', msg.role]"
          >
            <el-avatar 
              v-if="msg.role === 'system'" 
              class="msg-avatar system-avatar" 
              :size="32"
            >
              AI
            </el-avatar>
            <div class="bubble">{{ msg.content }}</div>
            <el-avatar 
              v-if="msg.role === 'user'" 
              class="msg-avatar user-avatar" 
              :size="32"
              src="https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png"
            />
          </div>
        </div>

        <div class="chat-input-area">
          <el-input 
            v-model="message" 
            placeholder="随时提问，比如：为什么要压缩到0-1？" 
            @keyup.enter="sendMessage"
            class="glow-input"
          >
            <template #append>
              <el-button type="primary" @click="sendMessage">发送 🚀</el-button>
            </template>
          </el-input>
        </div>
      </aside>

      <!-- 右侧资源面板 -->
      <main class="resource-panel glass-panel">
        <el-tabs type="border-card" class="transparent-tabs">
          <el-tab-pane label="📖 讲义">
            <div class="content-block">
              <h3>逻辑回归核心机制</h3>
              <p>逻辑回归虽然名字里有“回归”，但它实际上是一个分类算法。它的核心是线性回归外面套了一个 Sigmoid 函数。</p>
              <div class="formula">
                y = 1 / (1 + e^-(wx+b))
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="💻 实操代码">
            <div class="content-block code-block">
              <div class="code-header">
                <span>python</span>
                <span class="copy-btn">复制</span>
              </div>
              <pre><code>from sklearn.linear_model import LogisticRegression
import numpy as np

# 创建模型
model = LogisticRegression()

# 训练模型
model.fit(X_train, y_train)</code></pre>
            </div>
          </el-tab-pane>
          <el-tab-pane label="🗺️ 知识图谱">
            <div class="graph-placeholder">
              <div class="node active">Python</div>
              <div class="line"></div>
              <div class="node active">线性代数</div>
              <div class="line"></div>
              <div class="node current">逻辑回归</div>
              <div class="line"></div>
              <div class="node locked">模型评估</div>
            </div>
          </el-tab-pane>
        </el-tabs>
      </main>
    </div>
  </div>
</template>

<style scoped>
.learning-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  padding: 1rem;
  gap: 1rem;
}

.glass-header {
  height: 60px;
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}

.logo {
  font-weight: 700;
  font-size: 1.2rem;
}
.logo span {
  color: var(--accent-cyan);
}

.status-center {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.9rem;
}
.label {
  color: var(--text-muted);
}
.value {
  color: var(--text-primary);
  font-weight: 500;
}
.active-value {
  color: var(--accent-cyan);
  text-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
}

.main-layout {
  flex: 1;
  display: flex;
  gap: 1rem;
  overflow: hidden;
}

.glass-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border-light);
  border-radius: 16px;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-panel {
  flex: 0 0 400px;
}

.resource-panel {
  flex: 1;
}

.panel-header {
  padding: 1rem;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-status {
  font-size: 0.8rem;
  color: var(--accent-cyan);
  display: flex;
  align-items: center;
  gap: 6px;
}

.dot {
  width: 6px;
  height: 6px;
  background-color: var(--accent-cyan);
  border-radius: 50%;
}
.pulse {
  box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.7);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0.7); }
  70% { box-shadow: 0 0 0 10px rgba(6, 182, 212, 0); }
  100% { box-shadow: 0 0 0 0 rgba(6, 182, 212, 0); }
}

.chat-history {
  flex: 1;
  padding: 1.5rem 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.message {
  display: flex;
  gap: 1rem;
  align-items: flex-end;
}
.message.user {
  justify-content: flex-end;
}

.system-avatar {
  background: linear-gradient(135deg, var(--accent-indigo), var(--accent-purple));
  color: white;
  font-size: 12px;
  box-shadow: var(--glow-shadow);
}

.bubble {
  padding: 0.8rem 1.2rem;
  border-radius: 12px;
  max-width: 75%;
  line-height: 1.5;
  font-size: 0.95rem;
}

.message.system .bubble {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  border-bottom-left-radius: 2px;
}

.message.user .bubble {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.15), rgba(99, 102, 241, 0.15));
  border: 1px solid rgba(6, 182, 212, 0.3);
  border-bottom-right-radius: 2px;
}

.chat-input-area {
  padding: 1rem;
  border-top: 1px solid var(--border-light);
}

/* 资源面板重置 Element Tabs 样式 */
:deep(.transparent-tabs) {
  background: transparent !important;
  border: none !important;
  height: 100%;
  display: flex;
  flex-direction: column;
}
:deep(.el-tabs__header) {
  background: rgba(0, 0, 0, 0.2) !important;
  border-bottom: 1px solid var(--border-light) !important;
}
:deep(.el-tabs__item) {
  color: var(--text-muted) !important;
  border: none !important;
}
:deep(.el-tabs__item.is-active) {
  background: transparent !important;
  color: var(--accent-cyan) !important;
  border-bottom: 2px solid var(--accent-cyan) !important;
}
:deep(.el-tabs__content) {
  flex: 1;
  overflow-y: auto;
  padding: 2rem !important;
}

.content-block {
  line-height: 1.8;
}
.content-block h3 {
  margin-bottom: 1rem;
  color: var(--text-primary);
}
.content-block p {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}
.formula {
  background: rgba(0, 0, 0, 0.5);
  padding: 1rem;
  border-radius: 8px;
  font-family: monospace;
  color: var(--accent-cyan);
  text-align: center;
  font-size: 1.2rem;
}

.code-block {
  background: #1e1e1e;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-light);
}
.code-header {
  background: #2d2d2d;
  padding: 0.5rem 1rem;
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: var(--text-muted);
}
.copy-btn {
  cursor: pointer;
  transition: color 0.3s;
}
.copy-btn:hover {
  color: var(--text-primary);
}
.code-block pre {
  margin: 0;
  padding: 1rem;
  color: #d4d4d4;
  font-family: 'Fira Code', monospace;
  overflow-x: auto;
}

.graph-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 2rem;
}
.node {
  padding: 0.8rem 1.5rem;
  border-radius: 20px;
  font-size: 0.9rem;
  border: 1px solid var(--border-light);
}
.node.active {
  background: rgba(6, 182, 212, 0.1);
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
}
.node.current {
  background: var(--accent-indigo);
  color: white;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
}
.node.locked {
  background: rgba(0, 0, 0, 0.3);
  color: var(--text-muted);
}
.line {
  width: 30px;
  height: 2px;
  background: var(--border-light);
}
</style>
