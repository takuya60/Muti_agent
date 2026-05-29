<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useLearnerStore } from '../stores/learner'
import { useGenerationStore } from '../stores/generation'

const router = useRouter()
const learnerStore = useLearnerStore()
const generationStore = useGenerationStore()
const theme = ref<'light' | 'dark'>('light')

const resource = computed(() => generationStore.currentResource?.generated_resources)
const currentNode = computed(() => resource.value?.current_focus_id)
const currentIndex = computed(() => resource.value?.current_step_index || 1)
const branches = computed(() => resource.value?.available_branches || [])

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

const markMastered = async (nodeId: string) => {
  const learner = learnerStore.currentLearner
  if (!learner) return
  learnerStore.currentLearner = {
    ...learner,
    mastered_points: Array.from(new Set([...(learner.mastered_points || []), nodeId])),
    knowledge_mastery: {
      ...(learner.knowledge_mastery || {}),
      [nodeId]: 0.9
    }
  }
  await generationStore.generateResource(learnerStore.currentLearner)
}

const switchBranch = async (branchId: string) => {
  const learner = learnerStore.currentLearner
  if (!learner) return
  const targetMap: Record<string, string> = {
    common_foundation: '共同基础',
    classification: '分类预测',
    regression: '连续值预测',
    model_explanation: '模型解释与集成',
    unsupervised: '无监督学习',
    deep_learning_intro: '深度学习入门'
  }
  learnerStore.currentLearner = {
    ...learner,
    target_direction: branchId,
    target_algorithm: targetMap[branchId] || '由系统推荐'
  }
  await generationStore.generateResource(learnerStore.currentLearner)
}
</script>

<template>
  <main class="path-page" :data-theme="theme">
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">AE</span>
        <div>
          <strong>AgentEdu</strong>
          <small>学习路径</small>
        </div>
      </div>
      <div class="top-actions">
        <button type="button" @click="router.push('/dashboard')">学习首页</button>
        <button type="button" @click="router.push('/learning')">当前关卡</button>
      </div>
    </header>

    <section class="hero panel">
      <p class="section-kicker">共同基础 + 多分支</p>
      <h1>你的路径不是一条固定直线。</h1>
      <p>{{ resource?.recommended_reason || '系统会根据画像、掌握点和目标方向推荐当前节点。' }}</p>
    </section>

    <section class="panel path-panel">
      <div class="section-header">
        <div>
          <p class="section-kicker">当前路线</p>
          <h2>{{ resource?.current_branch || '生成中' }}</h2>
        </div>
        <span>{{ currentIndex }} / {{ resource?.total_steps || 1 }}</span>
      </div>
      <div class="node-list">
        <article
          v-for="(node, idx) in resource?.learning_path || []"
          :key="resource?.learning_path_nodes?.[idx] || node"
          :class="['node-card', { current: resource?.learning_path_nodes?.[idx] === currentNode, done: Number(idx) + 1 < currentIndex }]"
        >
          <span>{{ Number(idx) + 1 }}</span>
          <div>
            <strong>{{ node }}</strong>
            <small v-if="resource?.learning_path_nodes?.[idx] === currentNode">当前推荐</small>
            <small v-else-if="Number(idx) + 1 < currentIndex">已掌握或已跳过</small>
            <small v-else>后续节点</small>
          </div>
          <button
            type="button"
            :disabled="generationStore.isGenerating || Number(idx) + 1 < currentIndex"
            @click="markMastered(resource?.learning_path_nodes?.[idx] || node)"
          >
            标记已掌握
          </button>
        </article>
      </div>
    </section>

    <section class="panel branch-panel">
      <p class="section-kicker">可切换分支</p>
      <h2>根据目标调整学习方向</h2>
      <div class="branch-grid">
        <article v-for="branch in branches" :key="branch.id" :class="['branch-card', { recommended: branch.recommended }]">
          <strong>{{ branch.title }}</strong>
          <p>{{ branch.description }}</p>
          <small>{{ branch.locked_reason || (branch.recommended ? '当前推荐方向' : '可以切换学习') }}</small>
          <div class="progress"><i :style="{ width: `${Math.round((branch.progress || 0) * 100)}%` }"></i></div>
          <button type="button" :disabled="generationStore.isGenerating || branch.recommended" @click="switchBranch(branch.id)">
            {{ branch.recommended ? '当前方向' : '切换到此分支' }}
          </button>
        </article>
      </div>
    </section>
  </main>
</template>

<style scoped>
:global(body) {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
}
.path-page {
  --bg: #f6f8fb;
  --panel: rgba(255, 255, 255, 0.88);
  --solid: #ffffff;
  --text: #0f172a;
  --muted: #64748b;
  --border: #e2e8f0;
  --primary: #4f46e5;
  --primary-soft: #eef2ff;
  --shadow: 0 18px 50px rgba(15, 23, 42, 0.09);
  min-height: 100dvh;
  color: var(--text);
  background: var(--bg);
}
.path-page[data-theme='dark'] {
  --bg: #111827;
  --panel: rgba(31, 41, 55, 0.88);
  --solid: #1f2937;
  --text: #f8fafc;
  --muted: #cbd5e1;
  --border: rgba(148, 163, 184, 0.22);
  --primary: #818cf8;
  --primary-soft: rgba(129, 140, 248, 0.16);
  --shadow: 0 22px 60px rgba(0, 0, 0, 0.30);
}
.panel,
.node-card,
.branch-card {
  border: 1px solid var(--border);
  background: var(--panel);
  box-shadow: var(--shadow);
}
.topbar,
.hero,
.path-panel,
.branch-panel {
  max-width: 1180px;
  margin-inline: auto;
}
.topbar {
  padding: 22px 20px 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
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
.brand small,
.node-card strong,
.node-card small,
.branch-card strong,
.branch-card small {
  display: block;
}
small,
p {
  color: var(--muted);
}
.top-actions {
  display: flex;
  gap: 10px;
}
button {
  min-height: 40px;
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
.hero,
.path-panel,
.branch-panel {
  margin-top: 24px;
  border-radius: 24px;
  padding: 28px;
}
h1 {
  max-width: 760px;
  margin: 0 0 12px;
  font-size: clamp(34px, 5vw, 56px);
  line-height: 1.04;
  letter-spacing: -0.05em;
}
h2 {
  margin: 0;
  letter-spacing: -0.03em;
}
.section-kicker {
  margin: 0 0 8px;
  color: var(--primary);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 18px;
}
.section-header > span {
  color: var(--primary);
  font-weight: 900;
}
.node-list {
  display: grid;
  gap: 10px;
}
.node-card {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) auto;
  align-items: center;
  gap: 14px;
  border-radius: 18px;
  padding: 14px;
  box-shadow: none;
}
.node-card > span {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: var(--primary);
  background: var(--primary-soft);
  font-weight: 900;
}
.node-card.current {
  border-color: var(--primary);
  background: var(--primary-soft);
}
.node-card.done {
  opacity: 0.72;
}
.branch-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
  margin-top: 16px;
}
.branch-card {
  border-radius: 18px;
  padding: 18px;
  box-shadow: none;
}
.branch-card.recommended {
  border-color: var(--primary);
  box-shadow: 0 12px 28px rgba(79, 70, 229, 0.12);
}
.progress {
  height: 8px;
  margin: 16px 0;
  border-radius: 999px;
  background: var(--primary-soft);
  overflow: hidden;
}
.progress i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--primary);
}
@media (max-width: 920px) {
  .topbar,
  .section-header {
    align-items: stretch;
    flex-direction: column;
  }
  .branch-grid {
    grid-template-columns: 1fr;
  }
  .node-card {
    grid-template-columns: 42px minmax(0, 1fr);
  }
  .node-card button {
    grid-column: 1 / -1;
  }
}
</style>
