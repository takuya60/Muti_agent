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

const agentSteps = [
  '画像诊断 Agent：分析学习基础',
  '路径规划 Agent：匹配知识图谱路径',
  '知识检索 Agent：查找知识库证据',
  '资源生成 Agent：生成讲义、代码和测验',
  '审核纠偏 Agent：检查难度、结构和引用',
  '反馈规划 Agent：给出下一步建议'
]

onMounted(async () => {
  const saved = localStorage.getItem('agentedu-theme') as 'light' | 'dark' | null
  if (saved) theme.value = saved
  if (!learnerStore.currentLearner) {
    router.push('/')
    return
  }
  if (!generationStore.currentResource) {
    await generationStore.generateResource(learnerStore.currentLearner)
  }
})

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('agentedu-theme', theme.value)
}

const continueLearning = async () => {
  if (!generationStore.currentResource && learnerStore.currentLearner) {
    await generationStore.generateResource(learnerStore.currentLearner)
  }
  router.push('/learning')
}

const refreshPlan = async () => {
  if (!learnerStore.currentLearner) return
  await generationStore.generateResource(learnerStore.currentLearner)
}

const profileLabel = (key: string, value?: string) => {
  const labels: Record<string, Record<string, string>> = {
    python_level: { none: '几乎没写过 Python', basic: '会基础语法', data_basic: '会 NumPy/Pandas', script: '能独立写脚本' },
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
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">AE</span>
        <div>
          <strong>AgentEdu</strong>
          <small>学习首页</small>
        </div>
      </div>
      <div class="top-actions">
        <button type="button" @click="activeDrawer = 'profile'">学习画像</button>
        <button type="button" @click="activeDrawer = 'agent'">Agent 过程</button>
        <button type="button" @click="activeDrawer = 'report'">阶段报告</button>
        <button type="button" @click="toggleTheme">{{ theme === 'light' ? '夜间模式' : '正常色调' }}</button>
      </div>
    </header>

    <section class="hero panel">
      <div>
        <p class="section-kicker">当前学习状态</p>
        <h1>{{ learner?.name || '学习者' }}，你的下一关是 {{ resource?.current_focus || '生成中' }}</h1>
        <p>{{ resource?.recommended_reason || '系统正在根据画像、知识图谱和知识库为你生成推荐路径。' }}</p>
        <p v-if="resource" :class="['mode-badge', resource.generation_mode]">
          生成模式：{{ resource.generation_mode === 'llm' ? 'LLM 生成' : 'Fallback 模板' }}
          <span v-if="resource.generation_error">｜{{ resource.generation_error }}</span>
        </p>
        <div class="hero-actions">
          <button class="primary-button" type="button" :disabled="generationStore.isGenerating" @click="continueLearning">
            {{ generationStore.isGenerating ? '生成中...' : '继续当前关卡' }}
          </button>
          <button type="button" :disabled="generationStore.isGenerating" @click="refreshPlan">重新生成推荐</button>
        </div>
      </div>
      <aside class="status-card">
        <span>{{ resource?.current_stage || '待诊断' }}</span>
        <strong>{{ progressPercent }}%</strong>
        <small>路径进度</small>
        <i :style="{ width: `${progressPercent}%` }"></i>
      </aside>
    </section>

    <section v-if="generationStore.isGenerating" class="agent-loading panel" aria-live="polite">
      <div class="spinner"></div>
      <div>
        <h2>多 Agent 正在协作生成学习资源</h2>
        <ul>
          <li v-for="step in agentSteps" :key="step">{{ step }}</li>
        </ul>
      </div>
    </section>

    <section class="grid">
      <article class="panel overview-card">
        <p class="section-kicker">推荐关卡</p>
        <h2>{{ resource?.current_focus || '等待生成' }}</h2>
        <dl>
          <div><dt>所在阶段</dt><dd>{{ resource?.current_stage || '-' }}</dd></div>
          <div><dt>当前分支</dt><dd>{{ resource?.current_branch || '-' }}</dd></div>
          <div><dt>下一关</dt><dd>{{ resource?.next_focus || '阶段复盘' }}</dd></div>
          <div><dt>已完成节点</dt><dd>{{ completedCount }}</dd></div>
        </dl>
      </article>

      <article class="panel feedback-card">
        <p class="section-kicker">最近反馈</p>
        <h2>{{ diagnosis?.recommended_level || learner?.current_level || 'beginner_plus' }}</h2>
        <p>{{ diagnosis?.explanation_strategy || '系统会根据你的画像调整讲义深度、代码解释粒度和测验难度。' }}</p>
        <div class="tags">
          <span v-for="point in diagnosis?.weak_points || []" :key="point">{{ point }}</span>
          <span v-if="!(diagnosis?.weak_points || []).length">暂无明显薄弱点</span>
        </div>
      </article>
    </section>

    <section class="panel branch-panel">
      <div class="section-header">
        <div>
          <p class="section-kicker">分支进度</p>
          <h2>共同基础 + 多分支路径</h2>
        </div>
        <button type="button" @click="router.push('/path')">查看完整路径</button>
      </div>
      <div class="branch-grid">
        <article v-for="branch in branches" :key="branch.id" :class="['branch-card', { recommended: branch.recommended }]">
          <div>
            <strong>{{ branch.title }}</strong>
            <small>{{ branch.recommended ? '系统推荐' : branch.locked_reason ? '建议先补基础' : '可选分支' }}</small>
          </div>
          <p>{{ branch.description }}</p>
          <div class="mini-progress"><i :style="{ width: `${Math.round((branch.progress || 0) * 100)}%` }"></i></div>
          <span>{{ Math.round((branch.progress || 0) * 100) }}%</span>
        </article>
        <p v-if="!branches.length" class="empty-text">资源生成完成后会显示分支进度。</p>
      </div>
    </section>

    <section class="panel report-strip">
      <div>
        <p class="section-kicker">阶段报告预览</p>
        <h2>{{ resource?.learning_report?.stage || resource?.current_stage || '暂无阶段' }}</h2>
        <p>{{ resource?.learning_report?.next_recommendation || '完成若干关卡后，系统会总结掌握点、薄弱点和下一阶段建议。' }}</p>
      </div>
      <button type="button" @click="activeDrawer = 'report'">打开报告</button>
    </section>

    <div v-if="activeDrawer" class="drawer-backdrop" @click="activeDrawer = null">
      <aside class="drawer panel" @click.stop>
        <header>
          <h2>{{ activeDrawer === 'profile' ? '学习画像' : activeDrawer === 'agent' ? 'Agent 协作过程' : '阶段报告' }}</h2>
          <button type="button" @click="activeDrawer = null">关闭</button>
        </header>

        <div v-if="activeDrawer === 'profile'" class="drawer-content">
          <dl>
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
            <span>{{ step.status }}</span>
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
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}
.dashboard {
  --bg: #f6f8fb;
  --panel: rgba(255, 255, 255, 0.88);
  --solid: #ffffff;
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
.dashboard[data-theme='dark'] {
  --bg: #111827;
  --panel: rgba(31, 41, 55, 0.88);
  --solid: #1f2937;
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
  border-radius: 24px;
  background: var(--panel);
  box-shadow: var(--shadow);
  backdrop-filter: blur(14px);
}
.topbar,
.hero,
.grid,
.branch-panel,
.report-strip,
.agent-loading {
  max-width: 1180px;
  margin-inline: auto;
}
.topbar {
  padding: 22px 20px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
}
.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  display: grid;
  place-items: center;
  color: #fff;
  background: var(--primary);
  font-weight: 900;
}
.brand strong,
.brand small {
  display: block;
}
.brand small,
p,
small,
dt,
.empty-text {
  color: var(--muted);
}
.top-actions,
.hero-actions,
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
button {
  min-height: 42px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 0 14px;
  color: var(--text);
  background: var(--solid);
  cursor: pointer;
}
button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}
.primary-button {
  color: #fff;
  border-color: var(--primary);
  background: var(--primary);
  font-weight: 800;
}
.hero {
  margin-top: 28px;
  padding: 32px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 220px;
  gap: 28px;
}
.section-kicker {
  margin: 0 0 8px;
  color: var(--primary);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
h1,
h2,
h3,
h4,
p {
  margin-top: 0;
}
h1 {
  margin-bottom: 14px;
  font-size: clamp(34px, 5vw, 56px);
  line-height: 1.02;
  letter-spacing: -0.05em;
}
h2 {
  letter-spacing: -0.03em;
}
.mode-badge {
  width: fit-content;
  border-radius: 999px;
  padding: 8px 12px;
  color: var(--primary);
  background: var(--primary-soft);
  font-weight: 800;
}
.mode-badge.fallback {
  color: #b45309;
  background: #fef3c7;
}
.status-card {
  border-radius: 22px;
  padding: 22px;
  background: var(--primary-soft);
  color: var(--primary);
}
.status-card span,
.status-card strong,
.status-card small {
  display: block;
}
.status-card strong {
  margin: 14px 0 2px;
  font-size: 46px;
  letter-spacing: -0.05em;
}
.status-card i,
.mini-progress i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--primary);
}
.status-card i {
  height: 8px;
  margin-top: 18px;
  border-radius: 999px;
}
.grid {
  margin-top: 18px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.overview-card,
.feedback-card,
.branch-panel,
.report-strip,
.agent-loading {
  padding: 24px;
}
dl {
  margin: 0;
}
dl div {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
}
dd {
  margin: 0;
  font-weight: 800;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.tags span,
.timeline span {
  border-radius: 999px;
  padding: 6px 10px;
  color: var(--primary);
  background: var(--primary-soft);
  font-size: 13px;
  font-weight: 800;
}
.agent-loading {
  margin-top: 18px;
  display: flex;
  gap: 18px;
  align-items: flex-start;
}
.spinner {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 4px solid var(--primary-soft);
  border-top-color: var(--primary);
  animation: spin 850ms linear infinite;
}
.branch-panel,
.report-strip {
  margin-top: 18px;
}
.section-header,
.report-strip {
  justify-content: space-between;
}
.branch-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 16px;
}
.branch-card {
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px;
  background: var(--solid);
}
.branch-card.recommended {
  border-color: var(--primary);
  box-shadow: 0 12px 28px rgba(79, 70, 229, 0.12);
}
.branch-card strong,
.branch-card small,
.branch-card > span {
  display: block;
}
.branch-card small,
.branch-card > span {
  color: var(--muted);
}
.mini-progress {
  height: 7px;
  border-radius: 999px;
  background: var(--primary-soft);
  overflow: hidden;
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
  width: min(460px, 92vw);
  height: 100%;
  border-radius: 24px 0 0 24px;
  overflow-y: auto;
}
.drawer header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 18px;
  border-bottom: 1px solid var(--border);
}
.drawer h2 {
  margin: 0;
}
.drawer-content {
  padding: 18px;
}
.timeline article {
  position: relative;
  padding: 0 0 18px 18px;
  border-left: 2px solid var(--border);
}
.timeline h3 {
  margin: 10px 0 8px;
}
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 920px) {
  .topbar,
  .hero,
  .report-strip,
  .agent-loading {
    flex-direction: column;
    align-items: stretch;
  }
  .hero,
  .grid,
  .branch-grid {
    grid-template-columns: 1fr;
  }
  .topbar {
    align-items: stretch;
  }
  .top-actions {
    flex-wrap: wrap;
  }
}
</style>
