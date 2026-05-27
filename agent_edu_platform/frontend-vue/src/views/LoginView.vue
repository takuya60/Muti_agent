<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useLearnerStore } from '../stores/learner'
import { ElMessage } from 'element-plus'

const router = useRouter()
const learnerStore = useLearnerStore()
const currentStep = ref(1)
const isBuilding = ref(false)

const formData = reactive({
  name: '',
  goal: '',
  background: '',
  stylePref: '',
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
  { label: '文科/商科 (无编程经验)', value: '文科商科小白' },
  { label: '理科生 (懂数学，没写过代码)', value: '理科无代码' },
  { label: '纯开发 (代码熟练，数学全忘)', value: '纯开发' },
  { label: 'AI交叉 (懂一点算法和代码)', value: 'AI交叉学科' }
]

const stylePrefs = [
  { label: '图解驱动 (喜欢看可视化图表)', value: '图解类比' },
  { label: '案例驱动 (喜欢看实际应用案例)', value: '案例驱动' },
  { label: '推导驱动 (严谨的数学公式推导)', value: '公式推导' },
  { label: '项目驱动 (直接写代码跑模型)', value: '项目挑战' }
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

const nextStep = () => {
  if (currentStep.value === 1 && (!formData.name || !formData.goal)) return
  if (currentStep.value === 2 && (!formData.background || !formData.stylePref)) return
  currentStep.value++
}

const prevStep = () => {
  currentStep.value--
}

const handleStart = async () => {
  if (!formData.level) {
    ElMessage.warning('请选择您的综合水平')
    return
  }
  
  isBuilding.value = true
  
  try {
    // 模拟构建延迟，展示科技感动画
    await new Promise(resolve => setTimeout(resolve, 2500))
    
    await learnerStore.login({
      learner_id: `user_${Date.now()}`,
      name: formData.name.trim(),
      goal: formData.goal,
      background: formData.background,
      preferred_style: formData.stylePref,
      current_level: formData.level,
      known_skills: formData.knownSkills,
      // 以下为自动生成的认知/情绪初始值，匹配企业级 Schema
      bloom_taxonomy: {},
      learning_style_model: { "preference": formData.stylePref },
      attention_span_minutes: 30,
      frustration_index: 0.0,
      engagement_score: 1.0,
      knowledge_mastery: Object.fromEntries(formData.knownSkills.map(s => [s, 0.8])) // 给勾选的技能赋初始掌握度 0.8
    })
    
    ElMessage.success('专属数字画像已就绪！进入学习空间')
    router.push('/learning')
  } catch (e) {
    ElMessage.error('画像生成失败，请重试')
    isBuilding.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="glow glow-1" :class="`glow-step-${currentStep}`"></div>
    <div class="glow glow-2" :class="`glow-step-${currentStep}`"></div>
    
    <div class="content-wrapper" v-if="!isBuilding">
      <div class="title-section">
        <h1 class="brand-title">Agent<span>Edu</span></h1>
        <p class="subtitle">新生多维能力评估 (Onboarding Wizard)</p>
      </div>

      <el-card class="glass-card wizard-card">
        <el-steps :active="currentStep" finish-status="success" align-center class="mb-6">
          <el-step title="基础识别" />
          <el-step title="背景自评" />
          <el-step title="能力摸底" />
        </el-steps>

        <!-- Step 1 -->
        <div v-show="currentStep === 1" class="step-content fade-in">
          <h2 class="step-title">第一步：识别身份与目标</h2>
          <div class="form-group">
            <label>你怎么称呼？</label>
            <el-input v-model="formData.name" placeholder="输入你的昵称" size="large" @keyup.enter="nextStep"/>
          </div>
          <div class="form-group">
            <label>你的核心目标是？</label>
            <div class="tags-grid">
              <el-tag v-for="goal in goals" :key="goal" 
                      :effect="formData.goal === goal ? 'dark' : 'plain'"
                      :class="['goal-tag', { 'active-tag': formData.goal === goal }]"
                      @click="formData.goal = goal">
                {{ goal }}
              </el-tag>
            </div>
          </div>
          <div class="step-actions right">
            <el-button type="primary" size="large" @click="nextStep" :disabled="!formData.name || !formData.goal">下一步：评估背景</el-button>
          </div>
        </div>

        <!-- Step 2 -->
        <div v-show="currentStep === 2" class="step-content fade-in">
          <h2 class="step-title">第二步：探究学习风格</h2>
          <div class="form-group">
            <label>你的真实专业背景属于？</label>
            <div class="tags-grid">
              <el-tag v-for="bg in backgrounds" :key="bg.value" 
                      :effect="formData.background === bg.value ? 'dark' : 'plain'"
                      :class="['goal-tag', { 'active-tag': formData.background === bg.value }]"
                      @click="formData.background = bg.value">
                {{ bg.label }}
              </el-tag>
            </div>
          </div>
          <div class="form-group">
            <label>当你遇到新概念时，你更喜欢哪种学习方式？</label>
            <div class="tags-grid">
              <el-tag v-for="style in stylePrefs" :key="style.value" 
                      :effect="formData.stylePref === style.value ? 'dark' : 'plain'"
                      :class="['goal-tag', { 'active-tag': formData.stylePref === style.value }]"
                      @click="formData.stylePref = style.value">
                {{ style.label }}
              </el-tag>
            </div>
          </div>
          <div class="step-actions space-between">
            <el-button size="large" @click="prevStep">上一步</el-button>
            <el-button type="primary" size="large" @click="nextStep" :disabled="!formData.background || !formData.stylePref">下一步：能力摸底</el-button>
          </div>
        </div>

        <!-- Step 3 -->
        <div v-show="currentStep === 3" class="step-content fade-in">
          <h2 class="step-title">第三步：知识锚点标定</h2>
          <div class="form-group">
            <label>请诚实地勾选你曾经“听说过或稍微了解”的技能：</label>
            <el-checkbox-group v-model="formData.knownSkills" class="skills-group">
              <el-checkbox v-for="skill in skillsList" :key="skill" :label="skill" border>
                {{ skill }}
              </el-checkbox>
            </el-checkbox-group>
          </div>
          <div class="form-group">
            <label>综合评估，你目前在“机器学习”领域的段位是：</label>
            <div class="tags-grid levels">
              <el-tag v-for="lvl in levels" :key="lvl.value" 
                      :effect="formData.level === lvl.value ? 'dark' : 'plain'"
                      :class="['goal-tag', { 'active-tag': formData.level === lvl.value }]"
                      @click="formData.level = lvl.value">
                {{ lvl.label }}
              </el-tag>
            </div>
          </div>
          <div class="step-actions space-between">
            <el-button size="large" @click="prevStep">上一步</el-button>
            <el-button type="primary" size="large" @click="handleStart" :disabled="!formData.level">生成专属数字画像 🚀</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 正在生成动画层 -->
    <div class="building-overlay" v-else>
      <div class="radar-spinner">
        <div class="radar-sweep"></div>
      </div>
      <h2>正在融合多维特征...</h2>
      <p class="typing-text">计算知识图谱锚点... 构建认知评估矩阵... 引擎即将就绪</p>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  position: relative;
  width: 100vw;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background: var(--bg-dark);
}

.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.4;
  transition: all 1s ease-in-out;
  animation: float 10s infinite alternate ease-in-out;
}
.glow-1 { width: 400px; height: 400px; top: -100px; left: -100px; }
.glow-2 { width: 500px; height: 500px; bottom: -200px; right: -100px; animation-delay: -5s; }

/* 随步骤动态切换背景光圈颜色，营造企业级氛围 */
.glow-step-1.glow-1 { background: var(--accent-purple); }
.glow-step-1.glow-2 { background: var(--accent-cyan); }
.glow-step-2.glow-1 { background: var(--accent-cyan); }
.glow-step-2.glow-2 { background: #3b82f6; } /* 蓝色 */
.glow-step-3.glow-1 { background: #10b981; } /* 翡翠绿 */
.glow-step-3.glow-2 { background: var(--accent-indigo); }

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(50px, 50px) scale(1.1); }
}

.content-wrapper {
  position: relative;
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2rem;
  width: 100%;
  max-width: 600px;
}

.brand-title {
  font-size: 3.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-align: center;
}
.brand-title span {
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-indigo));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.subtitle {
  color: var(--text-secondary);
  font-size: 1.1rem;
  text-align: center;
}

.glass-card {
  width: 100%;
  padding: 2.5rem 2rem;
  background: rgba(30, 30, 35, 0.6);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

.step-title {
  font-size: 1.3rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  text-align: center;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  padding-bottom: 1rem;
}

.form-group {
  margin-bottom: 2rem;
}
.form-group label {
  display: block;
  margin-bottom: 1rem;
  color: var(--text-secondary);
  font-size: 0.95rem;
  line-height: 1.4;
}

.tags-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.levels {
  grid-template-columns: repeat(4, 1fr);
  gap: 0.5rem;
}

.goal-tag {
  cursor: pointer;
  padding: 12px;
  height: auto;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-secondary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  text-align: center;
  white-space: normal;
  line-height: 1.3;
}
.goal-tag:hover {
  border-color: var(--accent-purple);
  color: var(--text-primary);
  transform: translateY(-2px);
}
.active-tag {
  background: linear-gradient(135deg, var(--accent-indigo), var(--accent-purple)) !important;
  color: white !important;
  border: none !important;
  box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
}

.skills-group {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}
.el-checkbox {
  margin-right: 0 !important;
  background: rgba(255,255,255,0.05);
  border-color: rgba(255,255,255,0.1) !important;
  color: var(--text-secondary);
  padding: 0 16px;
  height: 40px;
  border-radius: 8px;
}
.el-checkbox.is-checked {
  border-color: var(--accent-cyan) !important;
  background: rgba(45, 212, 191, 0.1);
}

.mb-6 { margin-bottom: 2rem; }

.step-actions {
  display: flex;
  margin-top: 2.5rem;
}
.step-actions.right { justify-content: flex-end; }
.step-actions.space-between { justify-content: space-between; }

.fade-in {
  animation: fadeIn 0.4s ease-out forwards;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateX(20px); }
  to { opacity: 1; transform: translateX(0); }
}

/* 构建动画层 */
.building-overlay {
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
}
.radar-spinner {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 2px solid rgba(16, 185, 129, 0.2);
  position: relative;
  overflow: hidden;
  margin-bottom: 2rem;
  box-shadow: 0 0 30px rgba(16, 185, 129, 0.2);
}
.radar-sweep {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: conic-gradient(from 0deg, transparent 70%, rgba(16, 185, 129, 0.8) 100%);
  border-radius: 50%;
  animation: radar-spin 2s linear infinite;
}
@keyframes radar-spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
.building-overlay h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
  background: linear-gradient(to right, #10b981, var(--accent-cyan));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.typing-text {
  color: var(--text-secondary);
  font-family: monospace;
  overflow: hidden;
  white-space: nowrap;
  border-right: 2px solid var(--accent-cyan);
  margin: 0 auto;
  animation: typing 2.5s steps(40, end), blink-caret .75s step-end infinite;
}
@keyframes typing {
  from { width: 0 }
  to { width: 100% }
}
@keyframes blink-caret {
  from, to { border-color: transparent }
  50% { border-color: var(--accent-cyan); }
}
</style>
