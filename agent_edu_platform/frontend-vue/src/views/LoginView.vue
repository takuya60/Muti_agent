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
  pythonLevel: '',
  mathLevel: '',
  mlLevel: '',
  practicePreference: '',
  theoryPreference: '',
  stylePref: '',
  targetDirection: 'system_recommended',
  currentConfusion: ''
})

const goals = [
  '系统入门机器学习',
  '完成一个小项目',
  '补齐课程/竞赛基础',
  '理解算法原理',
  '提升代码实战能力',
  '只是随便看看'
]

const pythonLevels = [
  { label: '几乎没写过 Python', value: 'none', desc: '从语法、变量、循环和函数开始补齐' },
  { label: '会基础语法', value: 'basic', desc: '能看懂变量、循环、函数，但数据处理不熟' },
  { label: '会 NumPy/Pandas', value: 'data_basic', desc: '能做基础数组运算和表格处理' },
  { label: '能独立写脚本', value: 'script', desc: '可以完成较完整的数据处理流程' }
]

const mathLevels = [
  { label: '害怕公式', value: 'fear_formula', desc: '希望少推导，多直觉、多例子' },
  { label: '基础概念可以', value: 'basic', desc: '能理解函数、比例、概率等基础概念' },
  { label: '学过线代/概率', value: 'college_math', desc: '能接受矩阵、概率和常见指标' },
  { label: '能接受推导', value: 'derivation', desc: '希望看到更完整的数学逻辑' }
]

const mlLevels = [
  { label: '完全没接触', value: 'none', desc: '先建立任务、数据、模型和评估的整体概念' },
  { label: '看过概念', value: 'concept', desc: '知道一些名词，但没形成实操闭环' },
  { label: '跑过 sklearn', value: 'sklearn_demo', desc: '能跟着示例训练模型，但不一定理解流程' },
  { label: '做过小项目', value: 'project', desc: '希望补系统性、调参和复盘能力' }
]

const practicePrefs = [
  { label: '先项目实践', value: 'project_first', desc: '先跑通任务，再解释背后的原理' },
  { label: '理论实践平衡', value: 'balanced', desc: '讲义、代码、测验都保持均衡' },
  { label: '先理解原理', value: 'theory_first', desc: '先建立概念框架，再进入代码' }
]

const theoryPrefs = [
  { label: '尽量少公式', value: 'low_formula' },
  { label: '多用直觉类比', value: 'intuitive' },
  { label: '可以接受公式', value: 'formula_ok' },
  { label: '希望完整推导', value: 'derivation' }
]

const stylePrefs = [
  { label: '图解类比', value: '图解类比' },
  { label: '案例驱动', value: '案例驱动' },
  { label: '公式推导', value: '公式推导' },
  { label: '项目挑战', value: '项目挑战' }
]

const targetDirections = [
  { label: '由系统推荐', value: 'system_recommended', desc: '先诊断画像，再推荐起点和分支' },
  { label: '先打共同基础', value: 'common_foundation', desc: '补齐 Python、数据处理和 sklearn 流程' },
  { label: '分类预测', value: 'classification', desc: '学习逻辑回归、树模型和分类指标' },
  { label: '连续值预测', value: 'regression', desc: '学习线性回归、误差指标和回归任务' },
  { label: '模型解释与集成', value: 'model_explanation', desc: '学习决策树、随机森林和特征重要性' },
  { label: '无监督探索', value: 'unsupervised', desc: '学习 PCA、KMeans、DBSCAN 和聚类评估' },
  { label: '深度学习入门', value: 'deep_learning_intro', desc: '学习神经网络、Keras 和早停正则化' }
]

const confusions = [
  '不知道从哪里开始',
  '看得懂教程但不会写代码',
  '公式看不懂',
  '不知道模型指标是什么意思',
  '学了很多但串不起来'
]

const stepTitle = computed(() => {
  if (currentStep.value === 1) return '学习目标'
  if (currentStep.value === 2) return '基础诊断'
  if (currentStep.value === 3) return '学习偏好'
  return '方向与困惑'
})

const stepDescription = computed(() => {
  if (currentStep.value === 1) return '先明确你的学习目的，系统会据此生成阶段任务和最终报告。'
  if (currentStep.value === 2) return '不要预设用户都有 Python 基础，系统会根据真实基础决定学习起点。'
  if (currentStep.value === 3) return '偏实践还是偏理论，会影响讲义结构、代码解释粒度和测验难度。'
  return '你可以指定方向，也可以让系统根据画像推荐共同基础或分支路线。'
})

const canContinue = computed(() => {
  if (currentStep.value === 1) return Boolean(formData.name.trim() && formData.goal)
  if (currentStep.value === 2) return Boolean(formData.pythonLevel && formData.mathLevel && formData.mlLevel)
  if (currentStep.value === 3) return Boolean(formData.practicePreference && formData.theoryPreference && formData.stylePref)
  return Boolean(formData.targetDirection)
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
  currentStep.value = Math.min(4, currentStep.value + 1)
}

const prevStep = () => {
  errorMessage.value = ''
  currentStep.value = Math.max(1, currentStep.value - 1)
}

const buildTestScores = () => {
  const pythonScores: Record<string, number> = { none: 25, basic: 50, data_basic: 75, script: 88 }
  const mathScores: Record<string, number> = { fear_formula: 35, basic: 58, college_math: 78, derivation: 90 }
  const mlScores: Record<string, number> = { none: 25, concept: 52, sklearn_demo: 76, project: 88 }

  return {
    python: pythonScores[formData.pythonLevel] ?? 50,
    linear_algebra: mathScores[formData.mathLevel] ?? 58,
    ml_basic: mlScores[formData.mlLevel] ?? 52,
    model_evaluation: formData.mlLevel === 'project' ? 78 : formData.mlLevel === 'sklearn_demo' ? 66 : 42
  }
}

const inferCurrentLevel = () => {
  if (formData.pythonLevel === 'script' && formData.mathLevel === 'derivation' && ['sklearn_demo', 'project'].includes(formData.mlLevel)) return 'advanced'
  if (['data_basic', 'script'].includes(formData.pythonLevel) && ['concept', 'sklearn_demo', 'project'].includes(formData.mlLevel)) return 'intermediate'
  return 'beginner_plus'
}

const directionToAlgorithm = () => {
  const map: Record<string, string> = {
    system_recommended: '由系统推荐',
    common_foundation: '共同基础',
    classification: '分类预测',
    regression: '连续值预测',
    model_explanation: '模型解释与集成',
    unsupervised: '无监督学习',
    deep_learning_intro: '深度学习入门'
  }
  return map[formData.targetDirection] || '由系统推荐'
}

const buildKnownSkills = () => {
  const skills: string[] = []
  if (['basic', 'data_basic', 'script'].includes(formData.pythonLevel)) skills.push('Python基础')
  if (['data_basic', 'script'].includes(formData.pythonLevel)) skills.push('Numpy/Pandas')
  if (['college_math', 'derivation'].includes(formData.mathLevel)) skills.push('线性代数', '概率论')
  if (['sklearn_demo', 'project'].includes(formData.mlLevel)) skills.push('逻辑回归')
  if (formData.targetDirection === 'deep_learning_intro') skills.push('深度学习')
  return Array.from(new Set(skills))
}

const handleStart = async () => {
  errorMessage.value = ''
  if (!canContinue.value) {
    errorMessage.value = '请选择目标方向。'
    return
  }

  isBuilding.value = true

  try {
    const knownSkills = buildKnownSkills()
    await learnerStore.login({
      learner_id: `user_${Date.now()}`,
      name: formData.name.trim(),
      goal: formData.goal,
      background: `Python=${formData.pythonLevel}；数学=${formData.mathLevel}；机器学习=${formData.mlLevel}`,
      preferred_style: formData.stylePref,
      target_algorithm: directionToAlgorithm(),
      target_direction: formData.targetDirection,
      python_level: formData.pythonLevel,
      math_level: formData.mathLevel,
      ml_level: formData.mlLevel,
      practice_preference: formData.practicePreference,
      theory_preference: formData.theoryPreference,
      current_confusion: formData.currentConfusion,
      test_scores: buildTestScores(),
      current_level: inferCurrentLevel(),
      known_skills: knownSkills,
      bloom_taxonomy: {},
      learning_style_model: {
        preference: formData.stylePref,
        practice_preference: formData.practicePreference,
        theory_preference: formData.theoryPreference
      },
      attention_span_minutes: 30,
      frustration_index: formData.currentConfusion ? 0.25 : 0.0,
      engagement_score: 1.0,
      knowledge_mastery: Object.fromEntries(knownSkills.map(s => [s, 0.8]))
    })

    router.push('/dashboard')
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
          <small>多 Agent 个性化实训平台</small>
        </div>
      </div>
      <button class="theme-button" type="button" @click="toggleTheme">
        {{ theme === 'light' ? '夜间模式' : '正常色调' }}
      </button>
    </header>

    <section class="layout">
      <aside class="intro-panel">
        <p class="section-kicker">学习画像诊断</p>
        <h1>先识别基础，再生成路径。</h1>
        <p class="intro-copy">
          系统不会假设你已经会 Python。多 Agent 会根据你的编程基础、数学基础、机器学习基础和偏好，决定从共同基础还是分支任务开始。
        </p>

        <div class="preview-card">
          <div class="preview-header">
            <span>闭环流程</span>
            <strong>AgentEdu</strong>
          </div>
          <ol>
            <li>画像诊断：识别 Python / 数学 / ML 基础</li>
            <li>路径规划：共同基础 + 多分支路线</li>
            <li>资源生成：讲义、代码、测验和常见错误</li>
            <li>反馈迭代：报告、掌握度和下一关推荐</li>
          </ol>
        </div>
      </aside>

      <section class="form-card" aria-label="学习画像表单">
        <div class="stepper" aria-label="填写进度">
          <span v-for="step in 4" :key="step" :class="['step-item', { active: step === currentStep, done: step < currentStep }]">
            {{ step }}
          </span>
        </div>

        <div v-if="isBuilding" class="loading-state" aria-live="polite">
          <div class="spinner"></div>
          <h2>正在建立学习画像</h2>
          <p>正在保存你的基础诊断和学习偏好...</p>
        </div>

        <template v-else>
          <div class="form-title">
            <span>Step {{ currentStep }} / 4</span>
            <h2>{{ stepTitle }}</h2>
            <p>{{ stepDescription }}</p>
          </div>

          <p v-if="errorMessage" class="error-message" role="alert">{{ errorMessage }}</p>

          <div v-show="currentStep === 1" class="form-step">
            <label class="field-label" for="learner-name">你的称呼</label>
            <input id="learner-name" v-model="formData.name" class="text-field" type="text" placeholder="例如：博丽灵梦" />

            <label class="field-label">学习目标</label>
            <div class="choice-grid two-col">
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
            <label class="field-label">Python 编程基础</label>
            <div class="choice-grid two-col">
              <button
                v-for="item in pythonLevels"
                :key="item.value"
                type="button"
                :class="['choice-card tall', { selected: formData.pythonLevel === item.value }]"
                @click="formData.pythonLevel = item.value"
              >
                <strong>{{ item.label }}</strong>
                <span>{{ item.desc }}</span>
              </button>
            </div>

            <label class="field-label">数学基础</label>
            <div class="choice-grid two-col">
              <button
                v-for="item in mathLevels"
                :key="item.value"
                type="button"
                :class="['choice-card tall', { selected: formData.mathLevel === item.value }]"
                @click="formData.mathLevel = item.value"
              >
                <strong>{{ item.label }}</strong>
                <span>{{ item.desc }}</span>
              </button>
            </div>

            <label class="field-label">机器学习基础</label>
            <div class="choice-grid two-col">
              <button
                v-for="item in mlLevels"
                :key="item.value"
                type="button"
                :class="['choice-card tall', { selected: formData.mlLevel === item.value }]"
                @click="formData.mlLevel = item.value"
              >
                <strong>{{ item.label }}</strong>
                <span>{{ item.desc }}</span>
              </button>
            </div>
          </div>

          <div v-show="currentStep === 3" class="form-step">
            <label class="field-label">实践 / 理论节奏</label>
            <div class="choice-grid two-col">
              <button
                v-for="item in practicePrefs"
                :key="item.value"
                type="button"
                :class="['choice-card tall', { selected: formData.practicePreference === item.value }]"
                @click="formData.practicePreference = item.value"
              >
                <strong>{{ item.label }}</strong>
                <span>{{ item.desc }}</span>
              </button>
            </div>

            <label class="field-label">理论深度</label>
            <div class="chip-row">
              <button
                v-for="item in theoryPrefs"
                :key="item.value"
                type="button"
                :class="['chip-button', { selected: formData.theoryPreference === item.value }]"
                @click="formData.theoryPreference = item.value"
              >
                {{ item.label }}
              </button>
            </div>

            <label class="field-label">解释风格</label>
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

          <div v-show="currentStep === 4" class="form-step">
            <label class="field-label">目标方向</label>
            <div class="choice-grid two-col">
              <button
                v-for="direction in targetDirections"
                :key="direction.value"
                type="button"
                :class="['choice-card tall', { selected: formData.targetDirection === direction.value }]"
                @click="formData.targetDirection = direction.value"
              >
                <strong>{{ direction.label }}</strong>
                <span>{{ direction.desc }}</span>
              </button>
            </div>

            <label class="field-label">当前最困惑的问题，可选</label>
            <div class="chip-row wrap">
              <button
                v-for="confusion in confusions"
                :key="confusion"
                type="button"
                :class="['chip-button', { selected: formData.currentConfusion === confusion }]"
                @click="formData.currentConfusion = formData.currentConfusion === confusion ? '' : confusion"
              >
                {{ confusion }}
              </button>
            </div>
          </div>

          <footer class="form-actions">
            <button type="button" class="secondary-button" :disabled="currentStep === 1" @click="prevStep">上一步</button>
            <button v-if="currentStep < 4" type="button" class="primary-button" @click="nextStep">下一步</button>
            <button v-else type="button" class="primary-button" @click="handleStart">生成画像并进入学习首页</button>
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
  --surface: rgba(255, 255, 255, 0.88);
  --surface-solid: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --border: rgba(148, 163, 184, 0.28);
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
  --surface: rgba(17, 24, 39, 0.86);
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
.chip-button {
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
  grid-template-columns: minmax(0, 0.82fr) minmax(460px, 580px);
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
  min-height: 720px;
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
.theme-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.08);
}
.choice-card.selected,
.chip-button.selected {
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
.chip-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 0 14px;
  color: var(--text);
  background: var(--surface-solid);
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

@media (max-width: 980px) {
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
  .choice-grid.two-col {
    grid-template-columns: 1fr;
  }
}
</style>
