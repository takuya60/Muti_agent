<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useLearnerStore } from '../stores/learner'
import { useGenerationStore } from '../stores/generation'
import { useRouter } from 'vue-router'

const router = useRouter()
const learnerStore = useLearnerStore()
const generationStore = useGenerationStore()

const message = ref('')
const chatHistory = ref<any[]>([
  { role: 'system', content: '你好！根据你的画像分析，我们已经为你规划了专属的学习路径。现在正在为你生成第一关的讲义...' }
])

const loadingTexts = ["正在检索知识库...", "正在为您生成专属题目...", "老师正在排版..."]
const currentLoadingText = ref(loadingTexts[0])
let loadingInterval: any = null

onMounted(async () => {
  if (!learnerStore.currentLearner) {
    router.push('/')
    return
  }
  
  loadingInterval = setInterval(() => {
    const idx = loadingTexts.indexOf(currentLoadingText.value)
    currentLoadingText.value = loadingTexts[(idx + 1) % loadingTexts.length]
  }, 2000)
  
  try {
    await generationStore.generateResource(learnerStore.currentLearner)
    chatHistory.value.push({ role: 'system', content: `讲义生成完毕！本次专注目标是：${generationStore.currentResource?.generated_resources?.title}。你可以随时提问。` })
  } finally {
    if (loadingInterval) clearInterval(loadingInterval)
  }
})

onUnmounted(() => {
  if (loadingInterval) clearInterval(loadingInterval)
})

const updateAssistantMessage = (index: number, content: string) => {
  chatHistory.value[index] = {
    ...chatHistory.value[index],
    content
  }
}

const appendAssistantMessage = (index: number, content: string) => {
  updateAssistantMessage(index, chatHistory.value[index].content + content)
}

const sendMessage = async () => {
  if (message.value.trim()) {
    const userMsg = message.value
    chatHistory.value.push({ role: 'user', content: userMsg })
    message.value = ''

    const aiIndex = chatHistory.value.length
    chatHistory.value.push({ role: 'system', content: '' })

    try {
      const sessionId = generationStore.currentResource?.session_id
      if (!sessionId) throw new Error("缺少 session_id，资源生成可能失败，请刷新重试")

      const response = await fetch(`http://localhost:8000/sessions/${sessionId}/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: 'user', content: userMsg })
      })

      if (!response.ok) throw new Error(`Stream error: ${response.status}`)
      if (!response.body) throw new Error("后端没有返回可读取的流")

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ""
      let streamDone = false

      while (!streamDone) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })

        const parts = buffer.split('\n\n')
        buffer = parts.pop() || ""

        for (const part of parts) {
          if (part.startsWith('data: ')) {
            const dataStr = part.replace('data: ', '')
            try {
              const dataObj = JSON.parse(dataStr)
              if (dataObj.done) {
                streamDone = true
                break
              }
              appendAssistantMessage(aiIndex, dataObj.content || '')
            } catch (e) {
              appendAssistantMessage(aiIndex, `\n[消息解析失败：${e instanceof Error ? e.message : String(e)}]`)
            }
          }
        }
      }

      if (!chatHistory.value[aiIndex].content) {
        updateAssistantMessage(aiIndex, '（连接被中断，这可能是因为后台服务发生热更新，请重试）')
      }
    } catch (e) {
      updateAssistantMessage(aiIndex, `请求失败：${e instanceof Error ? e.message : '未知错误，请稍后再试'}`)
    }
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
        <span class="value">{{ learnerStore.currentLearner?.target_algorithm || '未知算法' }}</span>
        <el-divider direction="vertical" />
        <span class="label">级别：</span>
        <span class="value active-value">{{ learnerStore.currentLearner?.current_level || 'beginner' }}</span>
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
        <div v-if="generationStore.isGenerating" class="skeleton-container">
          <h3 class="loading-text pulse-text">{{ currentLoadingText }}</h3>
          <el-skeleton :rows="6" animated />
          <br/><br/>
          <el-skeleton :rows="4" animated />
        </div>

        <el-tabs v-else-if="generationStore.currentResource?.generated_resources" type="border-card" class="transparent-tabs">
          <el-tab-pane label="📖 讲义">
            <div class="content-block">
              <h3>{{ generationStore.currentResource.generated_resources.title }}</h3>
              <div class="generation-meta">
                <el-tag
                  :type="generationStore.currentResource.generated_resources.generation_mode === 'llm' ? 'success' : 'warning'"
                  effect="dark"
                >
                  生成模式：{{ generationStore.currentResource.generated_resources.generation_mode || 'unknown' }}
                </el-tag>
                <el-tag v-if="generationStore.currentResource.session_id" effect="plain">
                  会话ID：{{ generationStore.currentResource.session_id }}
                </el-tag>
              </div>
              <el-alert
                v-if="generationStore.currentResource.generated_resources.generation_error"
                :title="generationStore.currentResource.generated_resources.generation_error"
                type="warning"
                show-icon
                :closable="false"
                class="generation-error"
              />
              <p>{{ generationStore.currentResource.generated_resources.theory_note }}</p>
              
              <h4 v-if="generationStore.currentResource.generated_resources.citations.length" class="citation-title">📚 引用参考</h4>
              <div class="citations">
                <el-tag 
                  v-for="cite in generationStore.currentResource.generated_resources.citations" 
                  :key="cite" 
                  effect="dark"
                  class="citation-tag"
                >
                  {{ cite }}
                </el-tag>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="💻 实操代码">
            <div class="content-block">
              <p>{{ generationStore.currentResource.generated_resources.dataset_instruction }}</p>
              <div v-for="(step, idx) in generationStore.currentResource.generated_resources.practice_guide" :key="idx" class="code-block-wrapper">
                <h4>Step {{ Number(idx) + 1 }}: {{ step.step_name }}</h4>
                <div class="code-block">
                  <div class="code-header">
                    <span>python</span>
                  </div>
                  <pre><code>{{ step.python_code }}</code></pre>
                </div>
                <p class="code-explanation">{{ step.explanation }}</p>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="📝 闯关评测">
            <div class="content-block">
              <div v-for="(quiz, idx) in generationStore.currentResource.generated_resources.graded_quiz" :key="idx" class="quiz-block">
                <h4>【{{ quiz.level }}】{{ quiz.question }}</h4>
                <p><strong>答案:</strong> {{ quiz.answer }}</p>
                <p class="quiz-explanation"><em>解析: {{ quiz.explanation }}</em></p>
              </div>
            </div>
          </el-tab-pane>
          <el-tab-pane label="🗺️ 学习路径">
            <div class="graph-placeholder">
              <template v-for="(node, idx) in generationStore.currentResource.generated_resources.learning_path" :key="idx">
                <div class="node" :class="{ 'current': Number(idx) === 0, 'locked': Number(idx) > 0 }">{{ node }}</div>
                <div v-if="Number(idx) < generationStore.currentResource.generated_resources.learning_path.length - 1" class="line"></div>
              </template>
            </div>
          </el-tab-pane>
        </el-tabs>
        
        <div v-else class="skeleton-container">
          <h3>暂无资源，请返回首页重新激活。</h3>
        </div>
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

.skeleton-container {
  padding: 3rem;
}
.loading-text {
  color: var(--accent-cyan);
  margin-bottom: 2rem;
}
.pulse-text {
  animation: fade-pulse 2s infinite;
}
@keyframes fade-pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; text-shadow: 0 0 10px rgba(6,182,212,0.5); }
  100% { opacity: 0.6; }
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
.content-block h3, .content-block h4 {
  margin-bottom: 1rem;
  color: var(--text-primary);
}
.content-block p {
  color: var(--text-secondary);
  margin-bottom: 1rem;
}

.generation-meta {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
.generation-error {
  margin-bottom: 1rem;
}

.citation-title {
  margin-top: 2rem;
  color: var(--accent-purple) !important;
}
.citations {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.citation-tag {
  background: rgba(99, 102, 241, 0.2);
  border: 1px solid var(--accent-purple);
  color: var(--text-primary);
}

.code-block-wrapper {
  margin-bottom: 2rem;
}
.code-explanation {
  margin-top: 0.5rem;
  font-size: 0.9rem;
  color: var(--accent-cyan) !important;
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
.code-block pre {
  margin: 0;
  padding: 1rem;
  color: #d4d4d4;
  font-family: 'Fira Code', monospace;
  overflow-x: auto;
}

.quiz-block {
  background: rgba(255,255,255,0.03);
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 1rem;
  border-left: 4px solid var(--accent-indigo);
}
.quiz-explanation {
  color: var(--text-muted) !important;
  font-size: 0.9rem;
}

.graph-placeholder {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem;
}
.node {
  padding: 0.8rem 1.5rem;
  border-radius: 20px;
  font-size: 0.9rem;
  border: 1px solid var(--border-light);
}
.node.current {
  background: var(--accent-indigo);
  color: white;
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.5);
  border-color: var(--accent-purple);
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
