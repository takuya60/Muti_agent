<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref } from 'vue'
import MarkdownIt from 'markdown-it'
import markdownItKatex from 'markdown-it-katex'
import DOMPurify from 'dompurify'
import 'katex/dist/katex.min.css'
import { useLearnerStore } from '../stores/learner'
import { useGenerationStore } from '../stores/generation'
import { useRouter } from 'vue-router'

const md = new MarkdownIt({
  html: false,
  linkify: true,
  breaks: true
}).use(markdownItKatex)

const router = useRouter()
const learnerStore = useLearnerStore()
const generationStore = useGenerationStore()

const theme = ref<'light' | 'dark'>('light')
const message = ref('')
const activeTab = ref<'note' | 'code' | 'quiz'>('note')
const activeDrawer = ref<'profile' | 'references' | null>(null)
const streamingIndex = ref<number | null>(null)
const chatHistoryRef = ref<HTMLElement | null>(null)
const chatHistory = ref<any[]>([
  { role: 'system', content: '你好，我会围绕当前关卡回答问题。你可以先阅读讲义，也可以直接提问。' }
])

const loadingTexts = ['正在诊断学习画像', '正在检索知识证据', '正在生成当前关卡', '正在整理讲义内容']
const currentLoadingText = ref(loadingTexts[0])
let loadingInterval: number | undefined

const currentResources = () => generationStore.currentResource?.generated_resources
const hasSession = () => Boolean(generationStore.currentResource?.session_id)
const currentFocus = () => currentResources()?.current_focus || currentResources()?.learning_path?.[0] || '待生成'
const currentFocusId = () => currentResources()?.current_focus_id || currentResources()?.learning_path_nodes?.[Math.max(0, currentStepIndex() - 1)] || currentFocus()
const finalTarget = () => currentResources()?.final_target || learnerStore.currentLearner?.target_algorithm || '未知目标'
const currentStepIndex = () => currentResources()?.current_step_index || 1
const totalSteps = () => currentResources()?.total_steps || currentResources()?.learning_path?.length || 1
const progressPercent = computed(() => Math.min(100, Math.round((currentStepIndex() / totalSteps()) * 100)))

const renderMarkdown = (source?: string) => DOMPurify.sanitize(md.render(source || ''))

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('agentedu-theme', theme.value)
}

const scrollChatToBottom = async () => {
  await nextTick()
  if (chatHistoryRef.value) chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
}

onMounted(async () => {
  const saved = localStorage.getItem('agentedu-theme') as 'light' | 'dark' | null
  if (saved) theme.value = saved

  if (!learnerStore.currentLearner) {
    router.push('/')
    return
  }

  loadingInterval = window.setInterval(() => {
    const idx = loadingTexts.indexOf(currentLoadingText.value)
    currentLoadingText.value = loadingTexts[(idx + 1) % loadingTexts.length]
  }, 1800)

  try {
    await generationStore.generateResource(learnerStore.currentLearner)
    chatHistory.value.push({
      role: 'system',
      content: `第一关已解锁：**${currentFocus()}**。终点目标是 **${finalTarget()}**，当前进度 ${currentStepIndex()} / ${totalSteps()}。`
    })
    await scrollChatToBottom()
  } finally {
    if (loadingInterval) window.clearInterval(loadingInterval)
  }
})

onUnmounted(() => {
  if (loadingInterval) window.clearInterval(loadingInterval)
})

const updateAssistantMessage = (index: number, content: string) => {
  chatHistory.value[index] = { ...chatHistory.value[index], content }
  scrollChatToBottom()
}

const appendAssistantMessage = (index: number, content: string) => {
  updateAssistantMessage(index, chatHistory.value[index].content + content)
}

const completeCurrentStep = async () => {
  const learner = learnerStore.currentLearner
  if (!learner || generationStore.isGenerating) return

  const focusId = currentFocusId()
  const masteredPoints = Array.from(new Set([...(learner.mastered_points || []), focusId]))
  const knowledgeMastery = {
    ...(learner.knowledge_mastery || {}),
    [focusId]: 0.9
  }

  learnerStore.currentLearner = {
    ...learner,
    mastered_points: masteredPoints,
    knowledge_mastery: knowledgeMastery
  }

  chatHistory.value.push({
    role: 'system',
    content: `已记录你完成了 **${currentFocus()}**。我正在为你解锁下一关。`
  })
  await generationStore.generateResource(learnerStore.currentLearner)
  chatHistory.value.push({
    role: 'system',
    content: `下一关已解锁：**${currentFocus()}**。当前进度 ${currentStepIndex()} / ${totalSteps()}。`
  })
  await scrollChatToBottom()
}

const sendMessage = async () => {
  if (!message.value.trim() || streamingIndex.value !== null || !hasSession()) return

  const userMsg = message.value.trim()
  chatHistory.value.push({ role: 'user', content: userMsg })
  message.value = ''

  const aiIndex = chatHistory.value.length
  chatHistory.value.push({ role: 'system', content: '' })
  streamingIndex.value = aiIndex
  await scrollChatToBottom()

  try {
    const sessionId = generationStore.currentResource?.session_id
    if (!sessionId) throw new Error('缺少 session_id，资源生成可能失败，请刷新重试')

    const response = await fetch(`http://localhost:8001/sessions/${sessionId}/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role: 'user', content: userMsg })
    })

    if (!response.ok) throw new Error(`Stream error: ${response.status}`)
    if (!response.body) throw new Error('后端没有返回可读取的流')

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let streamDone = false

    while (!streamDone) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })

      const parts = buffer.split('\n\n')
      buffer = parts.pop() || ''

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

    if (!chatHistory.value[aiIndex].content) updateAssistantMessage(aiIndex, '连接被中断，请重试。')
  } catch (e) {
    updateAssistantMessage(aiIndex, `请求失败：${e instanceof Error ? e.message : '未知错误，请稍后再试'}`)
  } finally {
    streamingIndex.value = null
  }
}
</script>

<template>
  <main class="workspace" :data-theme="theme">
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">AE</span>
        <div>
          <strong>AgentEdu</strong>
          <small>学习工作台</small>
        </div>
      </div>
      <div class="course-meta">
        <span>当前关卡：{{ currentFocus() }}</span>
        <span>终点：{{ finalTarget() }}</span>
        <span>{{ currentStepIndex() }} / {{ totalSteps() }}</span>
      </div>
      <div class="top-actions">
        <button type="button" class="complete-button" :disabled="generationStore.isGenerating || !currentResources()" @click="completeCurrentStep">
          完成本关，进入下一关
        </button>
        <button type="button" @click="activeDrawer = 'profile'">学习画像</button>
        <button type="button" @click="activeDrawer = 'references'">引用资料</button>
        <button type="button" @click="toggleTheme">{{ theme === 'light' ? '夜间模式' : '正常色调' }}</button>
      </div>
    </header>

    <section class="workspace-grid">
      <aside class="path-sidebar panel">
        <div class="sidebar-title">
          <span>学习路径</span>
          <strong>{{ progressPercent }}%</strong>
        </div>
        <div class="progress-bar"><i :style="{ width: `${progressPercent}%` }"></i></div>
        <div class="path-list">
          <article
            v-for="(node, idx) in currentResources()?.learning_path || []"
            :key="idx"
            :class="['path-item', { current: node === currentFocus(), locked: Number(idx) + 1 > currentStepIndex() }]"
          >
            <span>{{ Number(idx) + 1 }}</span>
            <div>
              <strong>{{ node }}</strong>
              <small v-if="node === currentFocus()">正在学习</small>
              <small v-else-if="Number(idx) + 1 > currentStepIndex()">后续解锁</small>
              <small v-else>已具备基础</small>
            </div>
          </article>
        </div>
      </aside>

      <section class="content-area panel">
        <div v-if="generationStore.isGenerating" class="loading-state" aria-live="polite">
          <div class="spinner"></div>
          <h2>{{ currentLoadingText }}</h2>
          <p>正在准备当前关卡内容...</p>
        </div>

        <template v-else-if="currentResources()">
          <div class="lesson-header">
            <div>
              <p class="section-kicker">当前关卡</p>
              <h1>{{ currentFocus() }}</h1>
              <span>终点目标：{{ finalTarget() }}</span>
            </div>
            <div class="lesson-status">
              <strong>{{ progressPercent }}%</strong>
              <span>路径进度</span>
            </div>
          </div>

          <nav class="tabs" aria-label="学习资源分类">
            <button :class="{ active: activeTab === 'note' }" @click="activeTab = 'note'">讲义</button>
            <button :class="{ active: activeTab === 'code' }" @click="activeTab = 'code'">实操</button>
            <button :class="{ active: activeTab === 'quiz' }" @click="activeTab = 'quiz'">测评</button>
          </nav>

          <section v-show="activeTab === 'note'" class="markdown-body" v-html="renderMarkdown(currentResources()?.theory_note)"></section>

          <section v-show="activeTab === 'code'" class="code-section">
            <div class="markdown-body" v-html="renderMarkdown(currentResources()?.dataset_instruction)"></div>
            <article v-for="(step, idx) in currentResources()?.practice_guide" :key="idx" class="code-card">
              <header>
                <span>Step {{ Number(idx) + 1 }}</span>
                <strong>{{ step.step_name }}</strong>
              </header>
              <pre><code>{{ step.python_code }}</code></pre>
              <div class="markdown-body compact" v-html="renderMarkdown(step.explanation)"></div>
            </article>
          </section>

          <section v-show="activeTab === 'quiz'" class="quiz-section">
            <article v-for="(quiz, idx) in currentResources()?.graded_quiz" :key="idx" class="quiz-card">
              <span>{{ quiz.level }}</span>
              <h3>{{ quiz.question }}</h3>
              <details>
                <summary>查看参考答案与解析</summary>
                <p><strong>答案：</strong>{{ quiz.answer }}</p>
                <div class="markdown-body compact" v-html="renderMarkdown(quiz.explanation)"></div>
              </details>
            </article>
          </section>
        </template>

        <div v-else class="loading-state">
          <h2>暂无资源</h2>
          <p>请返回首页重新建立画像。</p>
        </div>
      </section>

      <aside class="tutor-panel panel">
        <div class="tutor-header">
          <div>
            <strong>AI 导师</strong>
            <small>上下文：{{ currentFocus() }}</small>
          </div>
          <span :class="['reply-state', { active: streamingIndex !== null }]">
            {{ streamingIndex !== null ? '回复中' : '在线' }}
          </span>
        </div>

        <div ref="chatHistoryRef" class="chat-history">
          <article
            v-for="(msg, index) in chatHistory"
            :key="index"
            :class="['message', msg.role, { streaming: streamingIndex === index }]"
          >
            <div class="message-content markdown-body compact" v-html="renderMarkdown(msg.content)"></div>
            <span v-if="streamingIndex === index" class="stream-cursor"></span>
          </article>
        </div>

        <form class="chat-input" @submit.prevent="sendMessage">
          <label class="sr-only" for="chat-message">向 AI 导师提问</label>
          <textarea
            id="chat-message"
            v-model="message"
            :disabled="streamingIndex !== null || !hasSession()"
            rows="2"
            :placeholder="hasSession() ? '围绕当前关卡提问...' : '资源生成完成后才能提问'"
            @keydown.enter.exact.prevent="sendMessage"
          ></textarea>
          <button type="submit" :disabled="!message.trim() || streamingIndex !== null || !hasSession()">发送</button>
        </form>
      </aside>
    </section>

    <div v-if="activeDrawer" class="drawer-backdrop" @click="activeDrawer = null">
      <aside class="drawer panel" @click.stop>
        <header>
          <h2>{{ activeDrawer === 'profile' ? '学习画像' : '引用资料' }}</h2>
          <button type="button" @click="activeDrawer = null">关闭</button>
        </header>

        <div v-if="activeDrawer === 'profile'" class="drawer-content">
          <dl>
            <div><dt>姓名</dt><dd>{{ learnerStore.currentLearner?.name || '-' }}</dd></div>
            <div><dt>背景</dt><dd>{{ learnerStore.currentLearner?.background || '-' }}</dd></div>
            <div><dt>目标</dt><dd>{{ learnerStore.currentLearner?.goal || '-' }}</dd></div>
            <div><dt>偏好</dt><dd>{{ learnerStore.currentLearner?.preferred_style || '-' }}</dd></div>
            <div><dt>水平</dt><dd>{{ learnerStore.currentLearner?.current_level || '-' }}</dd></div>
          </dl>
        </div>

        <div v-else class="drawer-content">
          <article v-for="cite in currentResources()?.citations || []" :key="cite" class="reference-item">
            {{ cite }}
          </article>
          <p v-if="!currentResources()?.citations?.length">暂无引用资料。</p>
        </div>
      </aside>
    </div>
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.workspace {
  --bg: #f6f8fb;
  --panel: #ffffff;
  --panel-soft: rgba(255, 255, 255, 0.82);
  --text: #0f172a;
  --muted: #64748b;
  --border: #e2e8f0;
  --primary: #4f46e5;
  --primary-soft: #eef2ff;
  --success: #16a34a;
  --shadow: 0 18px 50px rgba(15, 23, 42, 0.09);
  min-height: 100dvh;
  color: var(--text);
  background: var(--bg);
}
.workspace[data-theme='dark'] {
  --bg: #111827;
  --panel: #1f2937;
  --panel-soft: rgba(31, 41, 55, 0.86);
  --text: #f8fafc;
  --muted: #cbd5e1;
  --border: rgba(148, 163, 184, 0.22);
  --primary: #818cf8;
  --primary-soft: rgba(129, 140, 248, 0.16);
  --success: #22c55e;
  --shadow: 0 22px 60px rgba(0, 0, 0, 0.30);
}
.panel {
  border: 1px solid var(--border);
  background: var(--panel-soft);
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}
.topbar {
  height: 72px;
  display: grid;
  grid-template-columns: 220px minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  padding: 0 24px;
  border-bottom: 1px solid var(--border);
  background: var(--panel);
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.brand-mark {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #fff;
  background: var(--primary);
  font-weight: 800;
}
.brand strong,
.brand small,
.course-meta span {
  display: block;
}
.brand small,
.course-meta,
.reply-state,
.drawer dt {
  color: var(--muted);
}
.course-meta {
  display: flex;
  gap: 18px;
  overflow: hidden;
  white-space: nowrap;
}
.top-actions {
  display: flex;
  gap: 8px;
}
.complete-button {
  color: #fff;
  background: var(--success);
  border-color: var(--success);
  font-weight: 800;
}
button {
  min-height: 40px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0 14px;
  color: var(--text);
  background: var(--panel);
  cursor: pointer;
  transition: background 180ms ease, transform 180ms ease, border-color 180ms ease;
}
button:hover:not(:disabled) {
  transform: translateY(-1px);
  border-color: var(--primary);
}
button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}
button:focus-visible,
textarea:focus-visible {
  outline: 3px solid rgba(79, 70, 229, 0.22);
  outline-offset: 2px;
}
.workspace-grid {
  height: calc(100dvh - 72px);
  display: grid;
  grid-template-columns: 280px minmax(0, 1fr) 360px;
  gap: 18px;
  padding: 18px;
}
.path-sidebar,
.content-area,
.tutor-panel {
  min-height: 0;
  border-radius: 20px;
  overflow: hidden;
}
.path-sidebar,
.tutor-panel {
  display: flex;
  flex-direction: column;
}
.sidebar-title,
.tutor-header,
.drawer header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 18px;
  border-bottom: 1px solid var(--border);
}
.sidebar-title span,
.tutor-header strong {
  font-weight: 800;
}
.progress-bar {
  height: 8px;
  margin: 16px 18px;
  border-radius: 999px;
  background: var(--primary-soft);
  overflow: hidden;
}
.progress-bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--primary);
}
.path-list {
  padding: 0 14px 18px;
  overflow-y: auto;
}
.path-item {
  display: flex;
  gap: 12px;
  align-items: center;
  padding: 12px;
  border-radius: 14px;
  margin-bottom: 8px;
  border: 1px solid transparent;
}
.path-item > span {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 800;
}
.path-item strong,
.path-item small {
  display: block;
}
.path-item small {
  margin-top: 2px;
  color: var(--muted);
}
.path-item.current {
  border-color: var(--primary);
  background: var(--primary-soft);
}
.path-item.locked {
  opacity: 0.58;
}
.content-area {
  padding: 22px;
  overflow-y: auto;
}
.lesson-header {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding-bottom: 18px;
  border-bottom: 1px solid var(--border);
}
.section-kicker {
  margin: 0 0 8px;
  color: var(--primary);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.lesson-header h1 {
  margin: 0 0 8px;
  font-size: 34px;
  letter-spacing: -0.04em;
}
.lesson-header span,
.lesson-status span {
  color: var(--muted);
}
.lesson-status {
  min-width: 112px;
  height: 90px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: var(--primary-soft);
  color: var(--primary);
}
.lesson-status strong,
.lesson-status span {
  display: block;
  text-align: center;
}
.lesson-status strong {
  font-size: 28px;
}
.tabs {
  display: flex;
  gap: 8px;
  margin: 18px 0;
}
.tabs button.active {
  color: #fff;
  background: var(--primary);
  border-color: var(--primary);
}
.markdown-body {
  color: var(--text);
  line-height: 1.85;
}
.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3) {
  margin: 22px 0 10px;
  line-height: 1.35;
}
.markdown-body :deep(p) {
  margin: 0 0 14px;
}
.markdown-body :deep(ul) {
  padding-left: 22px;
}
.markdown-body :deep(code) {
  border-radius: 6px;
  padding: 2px 6px;
  background: var(--primary-soft);
  color: var(--primary);
}
.markdown-body :deep(pre) {
  overflow-x: auto;
  border-radius: 14px;
  padding: 14px;
  background: #0f172a;
  color: #e2e8f0;
}
.markdown-body.compact {
  font-size: 14px;
}
.code-card,
.quiz-card {
  margin-bottom: 16px;
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px;
  background: var(--panel);
}
.code-card header {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 12px;
}
.code-card header span,
.quiz-card > span {
  color: var(--primary);
  font-weight: 800;
}
.code-card pre {
  overflow-x: auto;
  border-radius: 14px;
  padding: 14px;
  background: #0f172a;
  color: #e2e8f0;
}
details summary {
  min-height: 44px;
  cursor: pointer;
  color: var(--primary);
  font-weight: 800;
}
.tutor-header small {
  display: block;
  margin-top: 4px;
  color: var(--muted);
}
.reply-state.active {
  color: var(--success);
}
.chat-history {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 16px;
}
.message {
  width: fit-content;
  max-width: 90%;
  margin-bottom: 12px;
  border-radius: 16px;
  padding: 12px 14px;
  background: var(--panel);
  border: 1px solid var(--border);
  box-shadow: 0 8px 22px rgba(15, 23, 42, 0.05);
  animation: messageIn 180ms ease-out;
}
.message.user {
  margin-left: auto;
  color: #fff;
  background: var(--primary);
  border-color: var(--primary);
}
.message.user .markdown-body,
.message.user .markdown-body :deep(p),
.message.user .markdown-body :deep(strong),
.message.user .markdown-body :deep(em),
.message.user .markdown-body :deep(li) {
  color: #fff;
}
.message.user .markdown-body :deep(code) {
  color: #fff;
  background: rgba(255, 255, 255, 0.18);
}
.message.streaming {
  border-color: var(--success);
}
.stream-cursor {
  display: inline-block;
  width: 2px;
  height: 18px;
  margin-left: 4px;
  background: var(--success);
  vertical-align: -3px;
  animation: blink 900ms steps(2, end) infinite;
}
.chat-input {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  padding: 16px;
  border-top: 1px solid var(--border);
}
.chat-input textarea {
  resize: none;
  min-height: 48px;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 10px 12px;
  color: var(--text);
  background: var(--panel);
  font: inherit;
}
.chat-input button {
  color: #fff;
  background: var(--primary);
  border-color: var(--primary);
  font-weight: 800;
}
.loading-state {
  display: grid;
  min-height: 420px;
  place-items: center;
  text-align: center;
  color: var(--muted);
}
.spinner {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 4px solid var(--primary-soft);
  border-top-color: var(--primary);
  animation: spin 850ms linear infinite;
}
.drawer-backdrop {
  position: fixed;
  inset: 0;
  z-index: 20;
  display: flex;
  justify-content: flex-end;
  background: rgba(15, 23, 42, 0.28);
}
.drawer {
  width: min(420px, 92vw);
  height: 100%;
  border-radius: 20px 0 0 20px;
  overflow-y: auto;
}
.drawer h2 {
  margin: 0;
}
.drawer-content {
  padding: 18px;
}
.drawer dl {
  margin: 0;
}
.drawer dl div,
.reference-item {
  padding: 14px 0;
  border-bottom: 1px solid var(--border);
}
.drawer dt {
  font-size: 13px;
}
.drawer dd {
  margin: 6px 0 0;
}
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes blink { 0%, 45% { opacity: 1; } 46%, 100% { opacity: 0; } }
@keyframes messageIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
@media (max-width: 1180px) {
  .workspace-grid {
    grid-template-columns: 240px minmax(0, 1fr) 320px;
  }
}
@media (max-width: 980px) {
  .topbar {
    height: auto;
    grid-template-columns: 1fr;
    padding: 16px;
  }
  .course-meta {
    flex-wrap: wrap;
  }
  .workspace-grid {
    height: auto;
    grid-template-columns: 1fr;
  }
  .path-sidebar,
  .tutor-panel {
    min-height: 360px;
  }
}
</style>
