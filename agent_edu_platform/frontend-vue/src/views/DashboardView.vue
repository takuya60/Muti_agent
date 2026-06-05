<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useLearnerStore } from '../stores/learner'
import { useGenerationStore } from '../stores/generation'

const router = useRouter()
const learnerStore = useLearnerStore()
const generationStore = useGenerationStore()
const theme = ref<'light' | 'dark'>('light')
const activeDrawer = ref<'profile' | 'agent' | 'report' | null>(null)

const resource = computed(() => generationStore.currentResource?.generated_resources)
const diagnosis = computed(() => generationStore.currentResource?.diagnosis)
const evaluation = computed(() => generationStore.currentResource?.evaluation)
const learner = computed(() => learnerStore.currentLearner)
const branches = computed(() => resource.value?.available_branches || [])
const progressPercent = computed(() => {
  const current = resource.value?.current_step_index || 1
  const total = resource.value?.total_steps || 1
  return Math.min(100, Math.round((current / total) * 100))
})
const completedCount = computed(() => learner.value?.mastered_points?.length || 0)

import { watch, nextTick } from 'vue'

const agentSteps = [
  { id: 'diagnosis', agent: '画像诊断', desc: '分析基础与路径' },
  { id: 'retrieval', agent: '知识检索', desc: '查找本地知识库' },
  { id: 'generation', agent: '资源生成', desc: '生成核心内容' },
  { id: 'review', agent: '质量审核', desc: '执行交叉审查' },
  { id: 'feedback', agent: '阶段报告', desc: '评估与后续反馈' }
]

const isStepDone = (stepId: string) => {
  if (generationStore.activeNode === 'complete' || generationStore.activeNode === 'cache') return true
  const currentIndex = agentSteps.findIndex(s => s.id === generationStore.activeNode)
  const targetIndex = agentSteps.findIndex(s => s.id === stepId)
  // 如果没匹配到，说明可能是错误或还没开始
  if (currentIndex === -1) return false
  return targetIndex < currentIndex
}

const terminalRef = ref<HTMLElement | null>(null)
watch(() => generationStore.streamLogs.length, async () => {
  await nextTick()
  if (terminalRef.value) {
    const body = terminalRef.value.querySelector('.terminal-body')
    if (body) {
      body.scrollTop = body.scrollHeight
    }
  }
})

onMounted(async () => {
  const saved = localStorage.getItem('agentedu-theme') as 'light' | 'dark' | null
  if (saved) theme.value = saved
  if (!learnerStore.currentLearner) {
    router.push('/')
    return
  }
  if (!generationStore.currentResource) {
    await generationStore.generateResourceStream(learnerStore.currentLearner)
  }
})

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('agentedu-theme', theme.value)
}

const continueLearning = async () => {
  try {
    if (!generationStore.currentResource && learnerStore.currentLearner) {
      await generationStore.generateResourceStream(learnerStore.currentLearner)
    }
    router.push('/learning')
  } catch (e: any) {
    alert('生成学习资源失败：' + (e.message || '未知错误'))
  }
}

const refreshPlan = async () => {
  if (!learnerStore.currentLearner) return
  try {
    await generationStore.generateResourceStream(learnerStore.currentLearner)
  } catch (e: any) {
    alert('重新生成推荐失败：' + (e.message || '未知错误'))
  }
}

const profileLabel = (key: string, value?: string) => {
  const labels: Record<string, Record<string, string>> = {
    python_level: { none: '几乎没写过', basic: '会基础语法', data_basic: '会 NumPy/Pandas', script: '能独立写脚本' },
    math_level: { fear_formula: '害怕公式', basic: '基础概念可以', college_math: '学过线代/概率', derivation: '能接受推导' },
    ml_level: { none: '完全没接触', concept: '看过概念', sklearn_demo: '跑过 sklearn', project: '做过小项目' },
    practice_preference: { project_first: '先项目实践', balanced: '理论实践平衡', theory_first: '先理解原理' },
    theory_preference: { low_formula: '尽量少公式', intuitive: '多用直觉类比', formula_ok: '可以接受公式', derivation: '希望完整推导' }
  }
  return labels[key]?.[value || ''] || value || '-'
}
</script>

<template>
  <main class="dashboard" :data-theme="theme">
    <!-- ===== 顶部导航栏 ===== -->
    <nav class="topbar">
      <div class="brand">
        <span class="brand-mark">AE</span>
        <strong>AgentEdu</strong>
      </div>
      <div class="nav-links">
        <router-link to="/dashboard" class="nav-link active">首页</router-link>
        <router-link to="/path" class="nav-link">学习路径</router-link>
        <router-link to="/learning" class="nav-link">学习页</router-link>
      </div>
      <button class="icon-btn" type="button" @click="toggleTheme" :title="theme === 'light' ? '夜间模式' : '正常色调'">
        {{ theme === 'light' ? '🌙' : '☀️' }}
      </button>
    </nav>

    <!-- ===== Hero 区域 ===== -->
    <section class="hero panel">
      <div class="hero-body">
        <p class="kicker">当前学习状态</p>
        <h1>{{ learner?.name || '学习者' }}，你的下一关是<br><em>{{ resource?.current_focus || '生成中…' }}</em></h1>
        <p class="hero-desc">{{ resource?.recommended_reason || '系统正在根据画像、知识图谱和知识库为你生成推荐路径。' }}</p>
        <p v-if="resource" :class="['badge', resource.generation_mode]">
          生成模式：{{ resource.generation_mode === 'llm' ? 'LLM 生成' : 'Fallback 模板' }}
          <span v-if="resource.generation_error">｜{{ resource.generation_error }}</span>
        </p>
        <div class="hero-actions">
          <button class="btn-primary" type="button" :disabled="generationStore.isGenerating" @click="continueLearning">
            {{ generationStore.isGenerating ? '生成中…' : '继续当前关卡' }}
          </button>
          <button class="btn-outline" type="button" :disabled="generationStore.isGenerating" @click="refreshPlan">重新生成推荐</button>
        </div>
      </div>
      <aside class="progress-ring-card">
        <svg class="progress-ring" viewBox="0 0 120 120">
          <circle cx="60" cy="60" r="52" class="ring-bg" />
          <circle cx="60" cy="60" r="52" class="ring-fill" :style="{ strokeDashoffset: 327 - 327 * progressPercent / 100 }" />
        </svg>
        <div class="ring-label">
          <strong>{{ progressPercent }}%</strong>
          <small>路径进度</small>
        </div>
        <span class="ring-stage">{{ resource?.current_stage || '待诊断' }}</span>
      </aside>
    </section>

    <!-- ===== 生成中动画与实时终端 ===== -->
    <section v-if="generationStore.isGenerating" class="agent-loading panel" aria-live="polite">
      <div class="agent-status-header">
        <div class="spinner"></div>
        <div>
          <h2>多 Agent 正在协作生成学习资源</h2>
          <p class="desc">系统通过 LangGraph 构建的流水线，正在为您定制个性化路径...</p>
        </div>
      </div>
      
      <div class="agent-steps-row">
        <div 
          v-for="step in agentSteps" 
          :key="step.id" 
          class="step-item"
          :class="{
            'active': generationStore.activeNode === step.id,
            'done': isStepDone(step.id)
          }"
        >
          <div class="step-icon">
            <span v-if="isStepDone(step.id)" class="icon-done">✓</span>
            <span v-else-if="generationStore.activeNode === step.id" class="pulse-dot"></span>
            <span v-else class="icon-pending">·</span>
          </div>
          <div class="step-text">
            <strong>{{ step.agent }}</strong>
            <small>{{ step.desc }}</small>
          </div>
        </div>
      </div>

      <div class="terminal-logs" ref="terminalRef">
        <div class="terminal-header">
          <span class="dot red"></span>
          <span class="dot yellow"></span>
          <span class="dot green"></span>
          <span class="title">agent-execution-logs ~ bash</span>
        </div>
        <div class="terminal-body">
          <div 
            v-for="log in generationStore.streamLogs" 
            :key="log.id" 
            :class="['log-line', log.type]"
          >
            {{ log.text }}
          </div>
        </div>
      </div>
    </section>

    <!-- ===== 信息卡片网格 ===== -->
    <section class="card-grid">
      <!-- 推荐关卡 -->
      <article class="panel card">
        <p class="kicker">推荐关卡</p>
        <h2>{{ resource?.current_focus || '等待生成' }}</h2>
        <dl class="meta-list">
          <div><dt>所在阶段</dt><dd>{{ resource?.current_stage || '-' }}</dd></div>
          <div><dt>当前分支</dt><dd>{{ resource?.current_branch || '-' }}</dd></div>
          <div><dt>下一关</dt><dd>{{ resource?.next_focus || '阶段复盘' }}</dd></div>
          <div><dt>已完成</dt><dd>{{ completedCount }} 个节点</dd></div>
        </dl>
      </article>

      <!-- 学习画像 -->
      <article class="panel card">
        <div class="card-header">
          <p class="kicker">学习画像</p>
          <button class="btn-ghost" type="button" @click="activeDrawer = 'profile'">查看详情</button>
        </div>
        <div class="profile-tags">
          <span class="tag"><b>Python</b> {{ profileLabel('python_level', learner?.python_level) }}</span>
          <span class="tag"><b>数学</b> {{ profileLabel('math_level', learner?.math_level) }}</span>
          <span class="tag"><b>ML</b> {{ profileLabel('ml_level', learner?.ml_level) }}</span>
          <span class="tag"><b>实践</b> {{ profileLabel('practice_preference', learner?.practice_preference) }}</span>
          <span class="tag"><b>理论</b> {{ profileLabel('theory_preference', learner?.theory_preference) }}</span>
        </div>
      </article>

      <!-- 最近反馈 -->
      <article class="panel card">
        <p class="kicker">诊断反馈</p>
        <h3>{{ diagnosis?.recommended_level || learner?.current_level || 'beginner_plus' }}</h3>
        <p class="card-desc">{{ diagnosis?.explanation_strategy || '系统会根据你的画像调整讲义深度。' }}</p>
        <div class="weak-tags">
          <span v-for="point in diagnosis?.weak_points || []" :key="point" class="weak-tag">{{ point }}</span>
          <span v-if="!(diagnosis?.weak_points || []).length" class="weak-tag muted">暂无明显薄弱点</span>
        </div>
      </article>

      <!-- Agent 协作过程 -->
      <article class="panel card">
        <div class="card-header">
          <p class="kicker">Agent 协作过程</p>
          <button class="btn-ghost" type="button" @click="activeDrawer = 'agent'">查看详情</button>
        </div>
        <div class="agent-mini-timeline">
          <div v-for="(step, i) in agentSteps" :key="step.agent" class="agent-mini-step">
            <span class="agent-dot" :class="{ done: !generationStore.isGenerating }">{{ generationStore.isGenerating ? '⏳' : '✅' }}</span>
            <span>{{ step.agent }}</span>
            <span v-if="i < agentSteps.length - 1" class="agent-arrow">→</span>
          </div>
        </div>
      </article>
    </section>

    <!-- ===== 分支进度 ===== -->
    <section class="panel section-block">
      <div class="section-header">
        <div>
          <p class="kicker">分支进度</p>
          <h2>共同基础 + 多分支路径</h2>
        </div>
        <button class="btn-outline" type="button" @click="router.push('/path')">查看完整路径</button>
      </div>
      <div class="branch-grid">
        <article v-for="branch in branches" :key="branch.id" :class="['branch-card', { recommended: branch.recommended }]">
          <div class="branch-head">
            <strong>{{ branch.title }}</strong>
            <small>{{ branch.recommended ? '系统推荐' : branch.locked_reason ? '建议先补基础' : '可选分支' }}</small>
          </div>
          <p>{{ branch.description }}</p>
          <div class="mini-progress"><i :style="{ width: `${Math.round((branch.progress || 0) * 100)}%` }"></i></div>
          <span class="progress-num">{{ Math.round((branch.progress || 0) * 100) }}%</span>
        </article>
        <p v-if="!branches.length" class="empty-text">资源生成完成后会显示分支进度。</p>
      </div>
    </section>

    <!-- ===== 阶段报告 ===== -->
    <section class="panel section-block report-section">
      <div class="section-header">
        <div>
          <p class="kicker">阶段报告预览</p>
          <h2>{{ resource?.learning_report?.stage || resource?.current_stage || '暂无阶段' }}</h2>
        </div>
        <button class="btn-outline" type="button" @click="activeDrawer = 'report'">打开报告</button>
      </div>
      <p>{{ resource?.learning_report?.next_recommendation || '完成若干关卡后，系统会总结掌握点、薄弱点和下一阶段建议。' }}</p>
    </section>

    <!-- ===== 抽屉 ===== -->
    <Transition name="drawer-fade">
      <div v-if="activeDrawer" class="drawer-backdrop" @click="activeDrawer = null">
        <aside class="drawer panel" @click.stop>
          <header>
            <h2>{{ activeDrawer === 'profile' ? '学习画像' : activeDrawer === 'agent' ? 'Agent 协作过程' : '阶段报告' }}</h2>
            <button class="btn-ghost" type="button" @click="activeDrawer = null">✕</button>
          </header>

          <div v-if="activeDrawer === 'profile'" class="drawer-content">
            <dl class="meta-list">
              <div><dt>姓名</dt><dd>{{ learner?.name || '-' }}</dd></div>
              <div><dt>目标</dt><dd>{{ learner?.goal || '-' }}</dd></div>
              <div><dt>Python 基础</dt><dd>{{ profileLabel('python_level', learner?.python_level) }}</dd></div>
              <div><dt>数学基础</dt><dd>{{ profileLabel('math_level', learner?.math_level) }}</dd></div>
              <div><dt>机器学习基础</dt><dd>{{ profileLabel('ml_level', learner?.ml_level) }}</dd></div>
              <div><dt>实践偏好</dt><dd>{{ profileLabel('practice_preference', learner?.practice_preference) }}</dd></div>
              <div><dt>理论偏好</dt><dd>{{ profileLabel('theory_preference', learner?.theory_preference) }}</dd></div>
              <div><dt>当前困惑</dt><dd>{{ learner?.current_confusion || '-' }}</dd></div>
            </dl>
          </div>

          <div v-else-if="activeDrawer === 'agent'" class="drawer-content timeline">
            <article v-for="step in resource?.agent_trace?.steps || []" :key="`${step.agent}-${step.title}`">
              <span class="timeline-status">{{ step.status }}</span>
              <h3>{{ step.agent }}：{{ step.title }}</h3>
              <p>{{ step.summary }}</p>
              <ul v-if="step.details?.length">
                <li v-for="detail in step.details" :key="detail">{{ detail }}</li>
              </ul>
            </article>
            <p v-if="!resource?.agent_trace?.steps?.length">暂无 Agent 过程，生成学习资源后会显示。</p>
          </div>

          <div v-else class="drawer-content">
            <h3>{{ resource?.learning_report?.stage || '阶段报告' }}</h3>
            <p>{{ resource?.learning_report?.next_recommendation || '暂无报告内容。' }}</p>
            <h4>掌握较好</h4>
            <ul><li v-for="item in resource?.learning_report?.strengths || []" :key="item">{{ item }}</li></ul>
            <h4>仍需加强</h4>
            <ul><li v-for="item in resource?.learning_report?.weak_points || []" :key="item">{{ item }}</li></ul>
            <h4>质量指标</h4>
            <p>知识覆盖率：{{ evaluation?.knowledge_coverage ? Math.round(evaluation.knowledge_coverage * 100) + '%' : '-' }}</p>
            <p>难度匹配度：{{ evaluation?.difficulty_match ? Math.round(evaluation.difficulty_match * 100) + '%' : '-' }}</p>
          </div>
        </aside>
      </div>
    </Transition>
  </main>
</template>

<style scoped>
/* ===== 变量 ===== */
:global(body) {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}
.dashboard {
  --bg: #f4f6fa;
  --panel: rgba(255,255,255,0.92);
  --solid: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --border: #e2e8f0;
  --primary: #4f46e5;
  --primary-soft: #eef2ff;
  --success: #16a34a;
  --shadow: 0 16px 48px rgba(15,23,42,0.07);
  min-height: 100dvh;
  color: var(--text);
  background: var(--bg);
  padding-bottom: 40px;
}
.dashboard[data-theme='dark'] {
  --bg: #0f172a;
  --panel: rgba(30,41,59,0.92);
  --solid: #1e293b;
  --text: #f8fafc;
  --muted: #94a3b8;
  --border: rgba(148,163,184,0.18);
  --primary: #818cf8;
  --primary-soft: rgba(129,140,248,0.14);
  --success: #22c55e;
  --shadow: 0 20px 56px rgba(0,0,0,0.28);
}

/* ===== 通用组件 ===== */
.panel {
  border: 1px solid var(--border);
  border-radius: 20px;
  background: var(--panel);
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow);
}
.kicker {
  margin: 0 0 6px;
  color: var(--primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
h1, h2, h3, h4, p { margin-top: 0; }
h1 { margin-bottom: 12px; font-size: clamp(28px, 4vw, 44px); line-height: 1.15; letter-spacing: -0.04em; }
h1 em { color: var(--primary); font-style: normal; }
h2 { letter-spacing: -0.02em; margin-bottom: 10px; }

/* ===== 按钮 ===== */
button {
  border: none;
  cursor: pointer;
  font-family: inherit;
  transition: all 180ms ease;
}
.btn-primary {
  height: 44px;
  border-radius: 12px;
  padding: 0 22px;
  color: #fff;
  background: var(--primary);
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(79,70,229,0.22);
}
.btn-primary:hover { transform: translateY(-1px); box-shadow: 0 12px 28px rgba(79,70,229,0.32); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.btn-outline {
  height: 40px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0 16px;
  color: var(--text);
  background: var(--solid);
  font-weight: 600;
}
.btn-outline:hover { border-color: var(--primary); color: var(--primary); }
.btn-ghost {
  height: 36px;
  padding: 0 10px;
  border-radius: 8px;
  color: var(--primary);
  background: transparent;
  font-weight: 700;
  font-size: 13px;
}
.btn-ghost:hover { background: var(--primary-soft); }
.icon-btn {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--solid);
  font-size: 18px;
  display: grid;
  place-items: center;
}

/* ===== 顶部导航 ===== */
.topbar {
  max-width: 1200px;
  margin: 0 auto;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: auto;
}
.brand-mark {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #fff;
  background: var(--primary);
  font-weight: 900;
  font-size: 14px;
  box-shadow: 0 6px 18px rgba(79,70,229,0.28);
}
.brand strong { font-size: 17px; }
.nav-links {
  display: flex;
  gap: 4px;
  background: var(--solid);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 4px;
}
.nav-link {
  padding: 8px 16px;
  border-radius: 9px;
  color: var(--muted);
  text-decoration: none;
  font-weight: 600;
  font-size: 14px;
  transition: all 180ms;
}
.nav-link:hover { color: var(--text); }
.nav-link.router-link-active {
  color: var(--primary);
  background: var(--primary-soft);
}

/* ===== Hero ===== */
.hero {
  max-width: 1200px;
  margin: 8px auto 0;
  padding: 32px;
  display: grid;
  grid-template-columns: 1fr 180px;
  gap: 28px;
  align-items: center;
}
.hero-desc { color: var(--muted); line-height: 1.7; max-width: 600px; }
.badge {
  display: inline-block;
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 800;
  color: var(--primary);
  background: var(--primary-soft);
  margin-bottom: 8px;
}
.badge.fallback { color: #b45309; background: #fef3c7; }
.hero-actions { display: flex; gap: 12px; margin-top: 6px; }

/* 进度环 */
.progress-ring-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}
.progress-ring { width: 140px; height: 140px; }
.ring-bg { fill: none; stroke: var(--border); stroke-width: 8; }
.ring-fill {
  fill: none;
  stroke: var(--primary);
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 327;
  transform: rotate(-90deg);
  transform-origin: center;
  transition: stroke-dashoffset 600ms ease;
}
.ring-label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}
.progress-ring-card { position: relative; }
.ring-label { position: absolute; top: 46px; left: 50%; transform: translateX(-50%); text-align: center; }
.ring-label strong { display: block; font-size: 32px; letter-spacing: -0.04em; color: var(--primary); }
.ring-label small { color: var(--muted); font-size: 12px; }
.ring-stage { color: var(--muted); font-size: 13px; font-weight: 700; }

/* ===== 生成中 ===== */
.agent-loading {
  max-width: 1200px;
  margin: 16px auto 0;
  padding: 24px 28px;
  display: flex;
  gap: 20px;
  align-items: flex-start;
}
.spinner {
  width: 40px; height: 40px; flex-shrink: 0;
  border-radius: 50%;
  border: 4px solid var(--primary-soft);
  border-top-color: var(--primary);
  animation: spin 850ms linear infinite;
}
.agent-loading h2 { margin-bottom: 8px; font-size: 18px; }
.agent-loading ul { margin: 0; padding-left: 18px; color: var(--muted); line-height: 1.8; }

/* ===== 卡片网格 ===== */
.card-grid {
  max-width: 1200px;
  margin: 16px auto 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.card { padding: 24px; }
.card-header { display: flex; justify-content: space-between; align-items: flex-start; }
.card-desc { color: var(--muted); line-height: 1.6; }
.meta-list { margin: 0; }
.meta-list div {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}
.meta-list dt { color: var(--muted); }
.meta-list dd { margin: 0; font-weight: 700; }

/* 画像标签 */
.profile-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 4px; }
.tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  color: var(--text);
  background: var(--solid);
  border: 1px solid var(--border);
}
.tag b { color: var(--primary); font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; }

/* 薄弱点标签 */
.weak-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.weak-tag {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 700;
  color: var(--primary);
  background: var(--primary-soft);
}
.weak-tag.muted { color: var(--muted); background: var(--solid); border: 1px solid var(--border); }

/* Agent 迷你时间线 */
.agent-mini-timeline { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; margin-top: 4px; }
.agent-mini-step { display: inline-flex; align-items: center; gap: 4px; font-size: 13px; }
.agent-dot { font-size: 14px; }
.agent-arrow { color: var(--muted); margin: 0 2px; }

/* ===== 通用 Section ===== */
.section-block {
  max-width: 1200px;
  margin: 16px auto 0;
  padding: 24px 28px;
}
.section-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; }

/* 分支卡片 */
.branch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 14px;
  margin-top: 16px;
}
.branch-card {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px;
  background: var(--solid);
  transition: all 180ms;
}
.branch-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(15,23,42,0.08); }
.branch-card.recommended { border-color: var(--primary); box-shadow: 0 8px 24px rgba(79,70,229,0.10); }
.branch-head strong, .branch-head small { display: block; }
.branch-head small { color: var(--muted); margin-top: 2px; }
.branch-card > p { color: var(--muted); font-size: 13px; line-height: 1.5; margin-bottom: 10px; }
.mini-progress { height: 6px; border-radius: 999px; background: var(--primary-soft); overflow: hidden; }
.mini-progress i { display: block; height: 100%; border-radius: inherit; background: var(--primary); transition: width 400ms ease; }
.progress-num { font-size: 13px; color: var(--muted); font-weight: 700; margin-top: 4px; display: inline-block; }
.empty-text { color: var(--muted); }

/* 报告 */
.report-section p { color: var(--muted); line-height: 1.7; }

/* ===== 抽屉 ===== */
.drawer-backdrop {
  position: fixed; inset: 0; z-index: 30;
  display: flex; justify-content: flex-end;
  background: rgba(15,23,42,0.32);
}
.drawer {
  width: min(460px, 92vw);
  height: 100%;
  border-radius: 20px 0 0 20px;
  overflow-y: auto;
}
.drawer header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border);
}
.drawer h2 { margin: 0; }
.drawer-content { padding: 20px 24px; }
.timeline article {
  position: relative;
  padding: 0 0 18px 18px;
  border-left: 2px solid var(--border);
}
.timeline-status {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  color: var(--primary);
  background: var(--primary-soft);
}
.timeline h3 { margin: 8px 0 6px; }

/* ===== 动画 ===== */
@keyframes spin { to { transform: rotate(360deg); } }
.drawer-fade-enter-active, .drawer-fade-leave-active { transition: opacity 200ms ease; }
.drawer-fade-enter-active .drawer, .drawer-fade-leave-active .drawer { transition: transform 250ms ease; }
.drawer-fade-enter-from, .drawer-fade-leave-to { opacity: 0; }
.drawer-fade-enter-from .drawer { transform: translateX(100%); }
.drawer-fade-leave-to .drawer { transform: translateX(100%); }

/* ===== 响应式 ===== */
@media (max-width: 920px) {
  .hero { grid-template-columns: 1fr; }
  .progress-ring-card { flex-direction: row; gap: 16px; }
  .card-grid { grid-template-columns: 1fr; }
  .branch-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 600px) {
  .topbar { flex-wrap: wrap; }
  .nav-links { order: 3; width: 100%; justify-content: center; }
  .hero-actions { flex-direction: column; }
  .branch-grid { grid-template-columns: 1fr; }
  .agent-steps-row { flex-direction: column; align-items: flex-start; gap: 12px; }
}

/* ===== SSE Terminal & Agent Steps UI ===== */
.agent-loading {
  max-width: 1200px;
  margin: 16px auto 0;
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.agent-status-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}
.agent-status-header h2 { margin-bottom: 4px; font-size: 18px; }
.agent-status-header .desc { color: var(--muted); margin: 0; font-size: 14px; }
.spinner {
  width: 36px; height: 36px; flex-shrink: 0;
  border-radius: 50%;
  border: 3px solid var(--primary-soft);
  border-top-color: var(--primary);
  animation: spin 850ms linear infinite;
}

.agent-steps-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 16px 20px;
  background: var(--bg);
  border-radius: 12px;
  border: 1px solid var(--border);
  justify-content: space-between;
}
.step-item {
  display: flex;
  align-items: center;
  gap: 10px;
  opacity: 0.5;
  transition: opacity 0.3s ease;
}
.step-item.active { opacity: 1; }
.step-item.done { opacity: 0.8; }

.step-icon {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--solid);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}
.step-item.done .step-icon {
  background: var(--success);
  border-color: var(--success);
  color: white;
}
.step-item.active .step-icon {
  border-color: var(--primary);
  background: var(--primary-soft);
}
.pulse-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--primary);
  box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.7);
  animation: pulse-animation 1.5s infinite cubic-bezier(0.66, 0, 0, 1);
}
@keyframes pulse-animation {
  to { box-shadow: 0 0 0 10px rgba(79, 70, 229, 0); }
}

.step-text strong { display: block; font-size: 13px; color: var(--text); }
.step-text small { display: block; font-size: 11px; color: var(--muted); }

/* Terminal Logs */
.terminal-logs {
  background: #0f172a; /* Slate 900 */
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  border: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
}
.terminal-header {
  background: #1e293b; /* Slate 800 */
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.terminal-header .dot {
  width: 12px; height: 12px; border-radius: 50%;
}
.terminal-header .red { background: #ef4444; }
.terminal-header .yellow { background: #f59e0b; }
.terminal-header .green { background: #10b981; }
.terminal-header .title {
  margin-left: auto; margin-right: auto;
  font-family: monospace; font-size: 12px; color: #94a3b8;
}
.terminal-body {
  padding: 16px;
  height: 240px;
  overflow-y: auto;
  font-family: 'Fira Code', 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.6;
  scroll-behavior: smooth;
  color: #e2e8f0; /* 强制终端基础字体为浅色 */
}
.log-line {
  margin-bottom: 6px;
  word-break: break-all;
}
.log-line.running { color: #a78bfa; } /* 紫色 */
.log-line.info { color: #38bdf8; } /* 亮蓝色 */
.log-line.warning { color: #fbbf24; } /* 琥珀色 */
.log-line.success { color: #34d399; } /* 翡翠绿 */
.log-line.error { color: #f87171; } /* 红色 */

</style>
