<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const learnerName = ref('')
const selectedGoal = ref('')

const goals = [
  '零基础入门机器学习',
  '补全数学/代码短板',
  '备战算法工程师面试',
  '只是随便看看'
]

const handleStart = () => {
  if (learnerName.value.trim() && selectedGoal.value) {
    // 实际项目中这里应调用后端 API 注册学习者画像
    router.push('/learning')
  }
}
</script>

<template>
  <div class="login-page">
    <!-- 背景流光特效 -->
    <div class="glow glow-1"></div>
    <div class="glow glow-2"></div>
    
    <div class="content-wrapper">
      <div class="title-section">
        <h1 class="brand-title">Agent<span>Edu</span></h1>
        <p class="subtitle">面向未来的智能自适应学习空间</p>
      </div>

      <el-card class="glass-card">
        <h2 class="card-title">构建你的数字画像</h2>
        
        <div class="form-group">
          <label>你怎么称呼？</label>
          <el-input 
            v-model="learnerName" 
            placeholder="输入你的昵称" 
            size="large"
          />
        </div>

        <div class="form-group">
          <label>你的核心目标是？</label>
          <div class="goal-tags">
            <el-tag
              v-for="goal in goals"
              :key="goal"
              :effect="selectedGoal === goal ? 'dark' : 'plain'"
              :class="{ 'active-tag': selectedGoal === goal }"
              @click="selectedGoal = goal"
              class="goal-tag"
            >
              {{ goal }}
            </el-tag>
          </div>
        </div>

        <el-button 
          type="primary" 
          class="submit-btn" 
          size="large" 
          @click="handleStart"
          :disabled="!learnerName || !selectedGoal"
        >
          激活学习引擎 🚀
        </el-button>
      </el-card>
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
}

/* 动态背景光晕 */
.glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.5;
  animation: float 10s infinite alternate ease-in-out;
}
.glow-1 {
  width: 400px;
  height: 400px;
  background: var(--accent-purple);
  top: -100px;
  left: -100px;
}
.glow-2 {
  width: 500px;
  height: 500px;
  background: var(--accent-cyan);
  bottom: -200px;
  right: -100px;
  animation-delay: -5s;
}

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
  gap: 3rem;
  width: 100%;
  max-width: 480px;
}

.brand-title {
  font-size: 3.5rem;
  font-weight: 700;
  letter-spacing: -1px;
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
  padding: 1rem;
}

.card-title {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  text-align: center;
  font-weight: 600;
}

.form-group {
  margin-bottom: 1.5rem;
}
.form-group label {
  display: block;
  margin-bottom: 0.8rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.goal-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem;
}
.goal-tag {
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-light);
  color: var(--text-secondary);
  transition: all 0.3s ease;
}
.goal-tag:hover {
  border-color: var(--accent-purple);
  color: var(--text-primary);
}
.active-tag {
  background: linear-gradient(135deg, var(--accent-indigo), var(--accent-purple)) !important;
  color: white !important;
  border: none !important;
}

.submit-btn {
  width: 100%;
  margin-top: 1rem;
  height: 48px;
  font-size: 1.1rem;
}
</style>
