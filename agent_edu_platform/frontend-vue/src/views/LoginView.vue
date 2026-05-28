<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useLearnerStore } from '../stores/learner'

const router = useRouter()
const learnerStore = useLearnerStore()
const currentStep = ref(1)
const isBuilding = ref(false)
const errorMessage = ref('')
const theme = ref<'light' | 'dark'>('light')

const formData = reactive({
  name: '',
  goal: '',
  background: '',
  stylePref: '',
  targetAlgorithm: '逻辑回归',
  knownSkills: [] as string[],
  level: ''
})

const goals = [
  '零基础入门机器学习',
  '补全数学/代码短板',
  '备战算法工程师面试',
  '只是随便看看'
]

const backgrounds = [
  { label: '文科/商科', desc: '无编程经验，适合从案例和直觉开始', value: '文科商科小白' },
  { label: '理科生', desc: '数学基础较好，需要补代码实操', value: '理科无代码' },
  { label: '纯开发', desc: '代码熟练，需要补数学和算法理解', value: '纯开发' },
  { label: 'AI交叉', desc: '已有基础，适合更快推进实训', value: 'AI交叉学科' }
]

const stylePrefs = [
  { label: '图解类比', value: '图解类比' },
  { label: '案例驱动', value: '案例驱动' },
  { label: '公式推导', value: '公式推导' },
  { label: '项目挑战', value: '项目挑战' }
]

const targetAlgorithms = [
  { label: '逻辑回归', value: '逻辑回归', desc: '适合入门分类模型，路径完整清晰' },
  { label: '决策树', value: '决策树', desc: '适合理解规则划分和可解释模型' },
  { label: '线性回归', value: '线性回归', desc: '适合先理解连续值预测和线性模型' },
  { label: '无监督学习', value: '无监督学习', desc: '适合探索聚类、降维和数据结构发现' },
  { label: '深度学习入门', value: '深度学习入门', desc: '适合了解神经网络和 Keras 快速实验' }
]

const skillsList = [
  'Python基础', 'Numpy/Pandas', '微积分', '线性代数', '概率论', '逻辑回归', '深度学习'
]

const levels = [
  { label: '零基础小白', value: 'beginner' },
  { label: '略知皮毛', value: 'beginner_plus' },
  { label: '中等熟手', value: 'intermediate' },
  { label: '硬核极客', value: 'advanced' }
]

const stepTitle = computed(() => {
  if (currentStep.value === 1) return '基础目标'
  if (currentStep.value === 2) return '背景与偏好'
  return '知识锚点'
})

const stepDescription = computed(() => {
  if (currentStep.value === 1) return '先明确你希望完成的学习目标，系统会把目标拆成可推进的路径。'
  if (currentStep.value === 2) return '学习背景和偏好会影响讲义的解释方式、代码粒度和题目难度。'
  return '已掌握知识会决定你从哪一关开始，而不是所有人都从同一页开始。'
})

const canContinue = computed(() => {
  if (currentStep.value === 1) return Boolean(formData.name.trim() && formData.goal)
  if (currentStep.value === 2) return Boolean(formData.targetAlgorithm && formData.background && formData.stylePref)
  return Boolean(formData.level)
})

onMounted(() => {
  const saved = localStorage.getItem('agentedu-theme') as 'light' | 'dark' | null
  if (saved) theme.value = saved
})

const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('agentedu-theme', theme.value)
}

const nextStep = () => {
  errorMessage.value = ''
  if (!canContinue.value) {
    errorMessage.value = '请先完成当前步骤的必填项。'
    return
  }
  currentStep.value = Math.min(3, currentStep.value + 1)
}

const prevStep = () => {
  errorMessage.value = ''
  currentStep.value = Math.max(1, currentStep.value - 1)
}

const buildTestScores = () => {
  const baseScores: Record<string, number> = {
    beginner: 35,
    beginner_plus: 55,
    intermediate: 75,
    advanced: 90
  }
  const base = baseScores[formData.level] ?? 55
  const hasPython = formData.knownSkills.includes('Python基础') || formData.knownSkills.includes('Numpy/Pandas')
  const hasMath = formData.knownSkills.includes('线性代数') || formData.knownSkills.includes('微积分') || formData.knownSkills.includes('概率论')
  const hasMl = formData.knownSkills.includes('逻辑回归') || formData.knownSkills.includes('深度学习')

  return {
    python: Math.min(100, base + (hasPython ? 12 : -8)),
    linear_algebra: Math.min(100, base + (hasMath ? 10 : -10)),
    ml_basic: Math.min(100, base + (hasMl ? 12 : -10)),
    model_evaluation: Math.min(100, base + (hasMl ? 5 : -12))
  }
}

const handleStart = async () => {
  errorMessage.value = ''
  if (!canContinue.value) {
    errorMessage.value = '请选择您的综合水平。'
    return
  }

  isBuilding.value = true

  try {
    await learnerStore.login({
      learner_id: `user_${Date.now()}`,
      name: formData.name.trim(),
      goal: formData.goal,
      background: formData.background,
      preferred_style: formData.stylePref,
      target_algorithm: formData.targetAlgorithm,
      test_scores: buildTestScores(),
      current_level: formData.level,
      known_skills: formData.knownSkills,
      bloom_taxonomy: {},
      learning_style_model: { preference: formData.stylePref },
      attention_span_minutes: 30,
      frustration_index: 0.0,
      engagement_score: 1.0,
      knowledge_mastery: Object.fromEntries(formData.knownSkills.map(s => [s, 0.8]))
    })

    router.push('/learning')
  } catch (e) {
    errorMessage.value = '画像生成失败，请检查后端服务后重试。'
    isBuilding.value = false
  }
}
</script>

<template>
  <main class="onboarding-page" :data-theme="theme">
    <header class="app-header">
      <div class="brand">
        <span class="brand-mark">AE</span>
        <div>
          <strong>AgentEdu</strong>
          <small>个性化机器学习实训</small>
        </div>
      </div>
      <button class="theme-button" type="button" @click="toggleTheme">
        {{ theme === 'light' ? '夜间模式' : '正常色调' }}
      </button>
    </header>

    <section class="layout">
      <aside class="intro-panel">
        <p class="section-kicker">学习路径生成器</p>
        <h1>先诊断<br>再规划<br>再逐关学习</h1>
        <p class="intro-copy">
          系统会根据你的背景、目标和知识锚点，生成一条通向目标算法的实训路径。每次只解锁当前最合适的一关，并由右侧导师持续陪练。
        </p>

        <div class="preview-card">
          <div class="preview-header">
            <span>路径预览</span>
            <strong>示例</strong>
          </div>
          <ol>
            <li>建立学习画像</li>
            <li>识别当前薄弱点</li>
            <li>解锁当前关卡讲义</li>
            <li>实操代码与导师答疑</li>
          </ol>
        </div>
      </aside>

      <section class="form-card" aria-label="学习画像表单">
        <div class="stepper" aria-label="填写进度">
          <span v-for="step in 3" :key="step" :class="['step-item', { active: step === currentStep, done: step < currentStep }]">
            {{ step }}
          </span>
        </div>

        <div v-if="isBuilding" class="loading-state" aria-live="polite">
          <div class="spinner"></div>
          <h2>正在生成学习画像</h2>
          <p>正在分析目标、背景和知识锚点...</p>
        </div>

        <template v-else>
          <div class="form-title">
            <span>Step {{ currentStep }} / 3</span>
            <h2>{{ stepTitle }}</h2>
            <p>{{ stepDescription }}</p>
          </div>

          <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>

          <div v-show="currentStep === 1" class="form-step">
            <label class="field-label" for="learner-name">你的称呼</label>
            <input id="learner-name" v-model="formData.name" class="text-field" type="text" />

            <label class="field-label">核心目标</label>
            <div class="choice-grid">
              <button
                v-for="goal in goals"
                :key="goal"
                type="button"
                :class="['choice-card', { selected: formData.goal === goal }]"
                @click="formData.goal = goal"
              >
                {{ goal }}
              </button>
            </div>
          </div>

          <div v-show="currentStep === 2" class="form-step">
            <label class="field-label">阶段目标</label>
            <div class="choice-grid two-col">
              <button
                v-for="algorithm in targetAlgorithms"
                :key="algorithm.value"
                type="button"
                :class="['choice-card tall', { selected: formData.targetAlgorithm === algorithm.value }]"
                @click="formData.targetAlgorithm = algorithm.value"
              >
                <strong>{{ algorithm.label }}</strong>
                <span>{{ algorithm.desc }}</span>
              </button>
            </div>

            <label class="field-label">学习背景</label>
            <div class="choice-grid two-col">
              <button
                v-for="background in backgrounds"
                :key="background.value"
                type="button"
                :class="['choice-card tall', { selected: formData.background === background.value }]"
                @click="formData.background = background.value"
              >
                <strong>{{ background.label }}</strong>
                <span>{{ background.desc }}</span>
              </button>
            </div>

            <label class="field-label">偏好风格</label>
            <div class="chip-row">
              <button
                v-for="style in stylePrefs"
                :key="style.value"
                type="button"
                :class="['chip-button', { selected: formData.stylePref === style.value }]"
                @click="formData.stylePref = style.value"
              >
                {{ style.label }}
              </button>
            </div>
          </div>

          <div v-show="currentStep === 3" class="form-step">
            <label class="field-label">你已经接触过的知识</label>
            <div class="chip-row wrap">
              <label v-for="skill in skillsList" :key="skill" :class="['check-chip', { selected: formData.knownSkills.includes(skill) }]">
                <input v-model="formData.knownSkills" type="checkbox" :value="skill" />
                {{ skill }}
              </label>
            </div>

            <label class="field-label">综合水平</label>
            <div class="choice-grid level-grid">
              <button
                v-for="level in levels"
                :key="level.value"
                type="button"
                :class="['choice-card', { selected: formData.level === level.value }]"
                @click="formData.level = level.value"
              >
                {{ level.label }}
              </button>
            </div>
          </div>

          <footer class="form-actions">
            <button type="button" class="secondary-button" :disabled="currentStep === 1" @click="prevStep">上一步</button>
            <button v-if="currentStep < 3" type="button" class="primary-button" @click="nextStep">下一步</button>
            <button v-else type="button" class="primary-button" @click="handleStart">生成画像并开始</button>
          </footer>
        </template>
      </section>
    </section>
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}

.onboarding-page {
  --bg: #f6f8fb;
  --surface: rgba(255, 255, 255, 0.86);
  --surface-solid: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --border: rgba(148, 163, 184, 0.26);
  --primary: #4f46e5;
  --primary-soft: #eef2ff;
  --success: #16a34a;
  --shadow: 0 20px 60px rgba(15, 23, 42, 0.10);
  min-height: 100dvh;
  color: var(--text);
  background:
    radial-gradient(circle at 12% 12%, rgba(79, 70, 229, 0.10), transparent 26%),
    radial-gradient(circle at 86% 18%, rgba(14, 165, 233, 0.10), transparent 28%),
    var(--bg);
}

.onboarding-page[data-theme='dark'] {
  --bg: #111827;
  --surface: rgba(17, 24, 39, 0.84);
  --surface-solid: #1f2937;
  --text: #f8fafc;
  --muted: #cbd5e1;
  --border: rgba(148, 163, 184, 0.24);
  --primary: #818cf8;
  --primary-soft: rgba(129, 140, 248, 0.16);
  --success: #22c55e;
  --shadow: 0 24px 70px rgba(0, 0, 0, 0.30);
}

.app-header {
  max-width: 1180px;
  margin: 0 auto;
  padding: 24px 20px 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
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
  font-weight: 800;
  box-shadow: 0 10px 24px rgba(79, 70, 229, 0.28);
}
.brand strong,
.brand small {
  display: block;
}
.brand small {
  margin-top: 2px;
  color: var(--muted);
}

.theme-button,
.primary-button,
.secondary-button,
.choice-card,
.chip-button,
.check-chip {
  min-height: 44px;
  cursor: pointer;
  transition: background 180ms ease, border-color 180ms ease, transform 180ms ease, box-shadow 180ms ease;
}
.theme-button {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0 16px;
  color: var(--text);
  background: var(--surface);
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
}

.layout {
  max-width: 1180px;
  margin: 34px auto 0;
  padding: 0 20px 40px;
  display: grid;
  grid-template-columns: minmax(0, 0.9fr) minmax(420px, 540px);
  gap: 28px;
}

.intro-panel {
  padding: 32px 8px;
}
.section-kicker,
.form-title span,
.field-label {
  color: var(--primary);
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.intro-panel h1 {
  max-width: 680px;
  margin: 16px 0;
  font-size: clamp(38px, 6vw, 72px);
  line-height: 0.98;
  letter-spacing: -0.06em;
}
.intro-copy {
  max-width: 620px;
  color: var(--muted);
  font-size: 18px;
  line-height: 1.8;
}
.preview-card,
.form-card {
  border: 1px solid var(--border);
  background: var(--surface);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: var(--shadow);
}
.preview-card {
  max-width: 520px;
  margin-top: 32px;
  border-radius: 22px;
  padding: 22px;
}
.preview-header {
  display: flex;
  justify-content: space-between;
  color: var(--muted);
}
.preview-card ol {
  margin: 18px 0 0;
  padding-left: 22px;
  color: var(--text);
  line-height: 1.9;
}

.form-card {
  min-height: 640px;
  display: flex;
  flex-direction: column;
  border-radius: 28px;
  padding: 28px;
}
.stepper {
  display: flex;
  gap: 8px;
  margin-bottom: 28px;
}
.step-item {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 999px;
  color: var(--muted);
  border: 1px solid var(--border);
  background: var(--surface-solid);
}
.step-item.active,
.step-item.done {
  color: #fff;
  border-color: var(--primary);
  background: var(--primary);
}
.form-title h2 {
  margin: 8px 0;
  font-size: 30px;
  letter-spacing: -0.03em;
}
.form-title p,
.error-message {
  margin: 0;
}
.form-title p {
  color: var(--muted);
  line-height: 1.7;
}
.error-message {
  margin-top: 16px;
  border-radius: 14px;
  padding: 12px 14px;
  color: #b91c1c;
  background: #fee2e2;
}

.form-step {
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin-top: 26px;
}
.field-label {
  margin-top: 6px;
}
.text-field {
  min-height: 48px;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 0 14px;
  color: var(--text);
  background: var(--surface-solid);
  font-size: 16px;
  outline: none;
}
.text-field:focus,
.theme-button:focus-visible,
.choice-card:focus-visible,
.chip-button:focus-visible,
.check-chip:focus-within,
.primary-button:focus-visible,
.secondary-button:focus-visible {
  outline: 3px solid rgba(79, 70, 229, 0.22);
  outline-offset: 2px;
}
.choice-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
.choice-card {
  text-align: left;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  color: var(--text);
  background: var(--surface-solid);
}
.choice-card:hover,
.chip-button:hover,
.check-chip:hover,
.theme-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08);
}
.choice-card.selected,
.chip-button.selected,
.check-chip.selected {
  border-color: var(--primary);
  background: var(--primary-soft);
  box-shadow: 0 10px 26px rgba(79, 70, 229, 0.12);
}
.choice-card.tall {
  min-height: 104px;
}
.choice-card strong,
.choice-card span {
  display: block;
}
.choice-card span {
  margin-top: 6px;
  color: var(--muted);
  line-height: 1.5;
}
.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.chip-button,
.check-chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0 14px;
  color: var(--text);
  background: var(--surface-solid);
}
.check-chip input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}
.form-actions {
  margin-top: auto;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-top: 28px;
}
.primary-button,
.secondary-button {
  border: 0;
  border-radius: 14px;
  padding: 0 18px;
  font-weight: 700;
}
.primary-button {
  color: #fff;
  background: var(--primary);
  box-shadow: 0 12px 26px rgba(79, 70, 229, 0.24);
}
.secondary-button {
  color: var(--text);
  background: var(--surface-solid);
  border: 1px solid var(--border);
}
.secondary-button:disabled {
  cursor: not-allowed;
  opacity: 0.45;
}
.loading-state {
  margin: auto;
  text-align: center;
}
.spinner {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  border-radius: 50%;
  border: 4px solid var(--primary-soft);
  border-top-color: var(--primary);
  animation: spin 850ms linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 920px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .form-card {
    min-height: auto;
  }
}

@media (max-width: 560px) {
  .app-header,
  .form-actions {
    align-items: stretch;
    flex-direction: column;
  }
  .choice-grid,
  .choice-grid.two-col,
  .level-grid {
    grid-template-columns: 1fr;
  }
}
</style>
