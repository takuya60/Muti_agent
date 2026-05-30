<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useLearnerStore } from '../stores/learner'
import { apiClient } from '../api'

const router = useRouter()
const learnerStore = useLearnerStore()
const theme = ref<'light' | 'dark'>('light')
const isLoading = ref(false)

interface TreeNode {
  id: string
  name: string
  mastered: boolean
  is_current: boolean
}
interface TreeBranch {
  id: string
  title: string
  description: string
  recommended: boolean
  progress: number
  locked_reason: string
  nodes: TreeNode[]
}
interface LearningTree {
  trunk: TreeNode[]
  branches: TreeBranch[]
  current_node: string
  current_node_name: string
  current_branch: string
  direction: string
  recommended_reason: string
}

const tree = ref<LearningTree | null>(null)
const expandedBranch = ref<string | null>(null)



const toggleTheme = () => {
  theme.value = theme.value === 'light' ? 'dark' : 'light'
  localStorage.setItem('agentedu-theme', theme.value)
}

onMounted(async () => {
  const saved = localStorage.getItem('agentedu-theme') as 'light' | 'dark' | null
  if (saved) theme.value = saved
  if (!learnerStore.currentLearner) {
    router.push('/')
    return
  }
  await loadTree()
})

const loadTree = async () => {
  if (!learnerStore.currentLearner) return
  isLoading.value = true
  try {
    const res = await apiClient.post('/learning-tree/tree', learnerStore.currentLearner)
    tree.value = res.data
    // 自动展开推荐分支
    if (tree.value) {
      const rec = tree.value.branches.find(b => b.recommended)
      if (rec) expandedBranch.value = rec.id
    }
  } catch (e) {
    console.error('[AgentEdu] 加载学习树失败', e)
  } finally {
    isLoading.value = false
  }
}

const toggleBranch = (branchId: string) => {
  expandedBranch.value = expandedBranch.value === branchId ? null : branchId
}

const switchBranch = async (branchId: string) => {
  if (!learnerStore.currentLearner) return
  isLoading.value = true
  try {
    const res = await apiClient.post('/learning-tree/switch-branch', {
      learner_profile: learnerStore.currentLearner,
      target_branch: branchId,
      target_algorithm: learnerStore.currentLearner.target_algorithm || '由系统推荐'
    })
    tree.value = res.data
    expandedBranch.value = branchId
    // 同步更新 store 中的 target_direction
    learnerStore.currentLearner = {
      ...learnerStore.currentLearner,
      target_direction: branchId
    }
  } catch (e) {
    console.error('[AgentEdu] 切换分支失败', e)
  } finally {
    isLoading.value = false
  }
}

const nodeStatus = (node: TreeNode) => {
  if (node.is_current) return 'current'
  if (node.mastered) return 'mastered'
  return 'locked'
}
</script>

<template>
  <main class="path-page" :data-theme="theme">
    <!-- 顶部导航 -->
    <nav class="topbar">
      <div class="brand">
        <span class="brand-mark">AE</span>
        <strong>AgentEdu</strong>
      </div>
      <div class="nav-links">
        <router-link to="/dashboard" class="nav-link">首页</router-link>
        <router-link to="/path" class="nav-link active">学习路径</router-link>
        <router-link to="/learning" class="nav-link">学习页</router-link>
      </div>
      <button class="icon-btn" type="button" @click="toggleTheme">
        {{ theme === 'light' ? '🌙' : '☀️' }}
      </button>
    </nav>

    <!-- Hero -->
    <section class="hero panel">
      <p class="kicker">个性化知识树</p>
      <h1>你的学习路径，不是一条直线</h1>
      <p class="hero-desc">{{ tree?.recommended_reason || '系统正在根据你的画像生成个性化学习路径。' }}</p>
    </section>

    <!-- 加载中 -->
    <section v-if="isLoading" class="loading-section panel">
      <div class="spinner"></div>
      <span>正在构建你的知识树…</span>
    </section>

    <!-- 知识树 -->
    <section v-else-if="tree" class="tree-section">
      <!-- ===== 主干 ===== -->
      <div class="tree-trunk">
        <div class="trunk-header">
          <div class="trunk-icon">🌱</div>
          <div>
            <p class="kicker">共同基础 · 主干</p>
            <h2>所有分支的根基</h2>
          </div>
        </div>
        <div class="trunk-track">
          <div class="track-line"></div>
          <div
            v-for="(node, i) in tree.trunk"
            :key="node.id"
            :class="['tree-node', nodeStatus(node)]"
          >
            <div class="node-dot">
              <span v-if="node.mastered">✓</span>
              <span v-else-if="node.is_current">●</span>
              <span v-else>{{ i + 1 }}</span>
            </div>
            <div class="node-info">
              <strong>{{ node.name }}</strong>
              <small v-if="node.is_current">← 当前推荐</small>
              <small v-else-if="node.mastered">已掌握</small>
            </div>
          </div>
        </div>
        <!-- 主干末端的分叉点 -->
        <div class="fork-point">
          <div class="fork-dot">⬦</div>
          <span>从这里开始分叉 →</span>
        </div>
      </div>

      <!-- ===== 分支 ===== -->
      <div class="branches-area">
        <div class="branches-header">
          <p class="kicker">学习分支</p>
          <h2>选择你的方向</h2>
        </div>

        <div class="branch-list">
          <article
            v-for="(branch, bi) in tree.branches"
            :key="branch.id"
            :class="['branch-block', { recommended: branch.recommended, expanded: expandedBranch === branch.id }]"
          >
            <!-- 分支头 -->
            <div class="branch-head" @click="toggleBranch(branch.id)">
              <div class="branch-color" :style="{ '--hue': 220 + bi * 45 + 'deg' }"></div>
              <div class="branch-meta">
                <strong>{{ branch.title }}</strong>
                <small>{{ branch.description }}</small>
              </div>
              <div class="branch-right">
                <span class="branch-progress">{{ Math.round(branch.progress * 100) }}%</span>
                <span v-if="branch.recommended" class="rec-badge">推荐</span>
                <button
                  v-else-if="!branch.locked_reason"
                  class="btn-switch"
                  type="button"
                  :disabled="isLoading"
                  @click.stop="switchBranch(branch.id)"
                >切换</button>
                <span v-else class="lock-badge">🔒</span>
              </div>
              <span class="expand-arrow">{{ expandedBranch === branch.id ? '▾' : '▸' }}</span>
            </div>

            <!-- 分支节点展开 -->
            <Transition name="expand">
              <div v-if="expandedBranch === branch.id" class="branch-nodes">
                <div class="branch-track" :style="{ '--hue': 220 + bi * 45 + 'deg' }">
                  <div class="track-line branch-line"></div>
                  <div
                    v-for="(node, ni) in branch.nodes"
                    :key="node.id"
                    :class="['tree-node', nodeStatus(node)]"
                  >
                    <div class="node-dot" :style="{ '--hue': 220 + bi * 45 + 'deg' }">
                      <span v-if="node.mastered">✓</span>
                      <span v-else-if="node.is_current">●</span>
                      <span v-else>{{ ni + 1 }}</span>
                    </div>
                    <div class="node-info">
                      <strong>{{ node.name }}</strong>
                      <small v-if="node.is_current">← 当前推荐</small>
                      <small v-else-if="node.mastered">已掌握</small>
                    </div>
                  </div>
                </div>
              </div>
            </Transition>

            <!-- 锁定提示 -->
            <p v-if="branch.locked_reason" class="lock-hint">{{ branch.locked_reason }}</p>
          </article>
        </div>
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
  --bg: #f4f6fa;
  --panel: rgba(255,255,255,0.92);
  --solid: #fff;
  --text: #0f172a;
  --muted: #64748b;
  --border: #e2e8f0;
  --primary: #4f46e5;
  --primary-soft: #eef2ff;
  --success: #16a34a;
  --success-soft: #dcfce7;
  --shadow: 0 16px 48px rgba(15,23,42,0.07);
  min-height: 100dvh;
  color: var(--text);
  background: var(--bg);
  padding-bottom: 60px;
}
.path-page[data-theme='dark'] {
  --bg: #0f172a;
  --panel: rgba(30,41,59,0.92);
  --solid: #1e293b;
  --text: #f8fafc;
  --muted: #94a3b8;
  --border: rgba(148,163,184,0.18);
  --primary: #818cf8;
  --primary-soft: rgba(129,140,248,0.14);
  --success: #22c55e;
  --success-soft: rgba(34,197,94,0.14);
  --shadow: 0 20px 56px rgba(0,0,0,0.28);
}
.panel { border: 1px solid var(--border); border-radius: 20px; background: var(--panel); backdrop-filter: blur(14px); box-shadow: var(--shadow); }
.kicker { margin: 0 0 4px; color: var(--primary); font-size: 12px; font-weight: 800; letter-spacing: 0.08em; text-transform: uppercase; }
h1, h2, h3, p { margin-top: 0; }
h1 { margin-bottom: 10px; font-size: clamp(28px, 4vw, 44px); line-height: 1.12; letter-spacing: -0.04em; }
h2 { letter-spacing: -0.02em; margin-bottom: 6px; }

/* ===== 导航 ===== */
.topbar { max-width: 1200px; margin: 0 auto; padding: 18px 24px; display: flex; align-items: center; gap: 16px; }
.brand { display: flex; align-items: center; gap: 10px; margin-right: auto; }
.brand-mark { width: 38px; height: 38px; border-radius: 12px; display: grid; place-items: center; color: #fff; background: var(--primary); font-weight: 900; font-size: 14px; box-shadow: 0 6px 18px rgba(79,70,229,0.28); }
.brand strong { font-size: 17px; }
.nav-links { display: flex; gap: 4px; background: var(--solid); border: 1px solid var(--border); border-radius: 12px; padding: 4px; }
.nav-link { padding: 8px 16px; border-radius: 9px; color: var(--muted); text-decoration: none; font-weight: 600; font-size: 14px; transition: all 180ms; }
.nav-link:hover { color: var(--text); }
.nav-link.router-link-active { color: var(--primary); background: var(--primary-soft); }
.icon-btn { width: 40px; height: 40px; border-radius: 12px; border: 1px solid var(--border); background: var(--solid); font-size: 18px; display: grid; place-items: center; cursor: pointer; }
button { border: none; cursor: pointer; font-family: inherit; transition: all 180ms; }

/* ===== Hero ===== */
.hero { max-width: 1200px; margin: 8px auto 0; padding: 32px; }
.hero-desc { color: var(--muted); line-height: 1.7; max-width: 600px; }

/* ===== 加载 ===== */
.loading-section { max-width: 1200px; margin: 20px auto 0; padding: 32px; display: flex; align-items: center; gap: 16px; }
.spinner { width: 36px; height: 36px; border-radius: 50%; border: 4px solid var(--primary-soft); border-top-color: var(--primary); animation: spin 850ms linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

/* ===== 知识树 ===== */
.tree-section { max-width: 1200px; margin: 20px auto 0; display: grid; grid-template-columns: 320px 1fr; gap: 20px; }

/* ===== 主干 ===== */
.tree-trunk { padding: 24px; border: 1px solid var(--border); border-radius: 20px; background: var(--panel); backdrop-filter: blur(14px); box-shadow: var(--shadow); }
.trunk-header { display: flex; gap: 14px; align-items: center; margin-bottom: 20px; }
.trunk-icon { font-size: 32px; }
.trunk-track { position: relative; padding-left: 20px; }
.track-line { position: absolute; left: 18px; top: 8px; bottom: 8px; width: 3px; background: var(--border); border-radius: 2px; }
.branch-track { position: relative; padding-left: 20px; }
.branch-line { background: hsl(var(--hue, 220deg) 70% 60% / 0.25); }

/* ===== 节点 ===== */
.tree-node { display: flex; align-items: center; gap: 14px; padding: 10px 0; position: relative; }
.node-dot {
  width: 36px; height: 36px; border-radius: 50%;
  display: grid; place-items: center;
  font-size: 13px; font-weight: 800;
  flex-shrink: 0; position: relative; z-index: 1;
  color: var(--muted); background: var(--solid); border: 2px solid var(--border);
  transition: all 250ms;
}
.tree-node.mastered .node-dot { color: var(--success); background: var(--success-soft); border-color: var(--success); }
.tree-node.current .node-dot {
  color: #fff; background: var(--primary); border-color: var(--primary);
  box-shadow: 0 0 0 6px rgba(79,70,229,0.18);
  animation: pulse 2s ease-in-out infinite;
}
.node-info strong { display: block; font-size: 14px; }
.node-info small { color: var(--muted); font-size: 12px; }
.tree-node.current .node-info strong { color: var(--primary); }

/* ===== 分叉点 ===== */
.fork-point { display: flex; align-items: center; gap: 10px; margin-top: 16px; padding: 12px 16px; border-radius: 12px; background: var(--primary-soft); }
.fork-dot { font-size: 18px; color: var(--primary); }
.fork-point span { font-size: 13px; font-weight: 700; color: var(--primary); }

/* ===== 分支区 ===== */
.branches-area { min-width: 0; }
.branches-header { margin-bottom: 16px; }
.branch-list { display: flex; flex-direction: column; gap: 12px; }

.branch-block {
  border: 1px solid var(--border);
  border-radius: 18px;
  background: var(--panel);
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow);
  overflow: hidden;
  transition: all 200ms;
}
.branch-block.recommended { border-color: var(--primary); box-shadow: 0 8px 28px rgba(79,70,229,0.10); }
.branch-block:hover { transform: translateY(-1px); }

.branch-head {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 20px; cursor: pointer;
  transition: background 150ms;
}
.branch-head:hover { background: rgba(0,0,0,0.02); }
.branch-color { width: 6px; height: 40px; border-radius: 3px; background: hsl(var(--hue, 220deg) 70% 60%); flex-shrink: 0; }
.branch-meta { flex: 1; min-width: 0; }
.branch-meta strong { display: block; font-size: 16px; }
.branch-meta small { color: var(--muted); font-size: 13px; }
.branch-right { display: flex; align-items: center; gap: 10px; }
.branch-progress { font-size: 20px; font-weight: 800; color: var(--primary); letter-spacing: -0.03em; }
.rec-badge { padding: 4px 10px; border-radius: 999px; font-size: 12px; font-weight: 800; color: var(--primary); background: var(--primary-soft); }
.lock-badge { font-size: 16px; }
.btn-switch {
  height: 34px; padding: 0 14px; border-radius: 10px;
  border: 1px solid var(--border); background: var(--solid);
  color: var(--text); font-weight: 600; font-size: 13px;
}
.btn-switch:hover { border-color: var(--primary); color: var(--primary); }
.expand-arrow { color: var(--muted); font-size: 14px; margin-left: 4px; }

.branch-nodes { padding: 0 20px 20px; }
.lock-hint { margin: 0; padding: 0 20px 16px; font-size: 13px; color: var(--muted); }

/* ===== 展开动画 ===== */
.expand-enter-active, .expand-leave-active { transition: all 250ms ease; overflow: hidden; }
.expand-enter-from, .expand-leave-to { opacity: 0; max-height: 0; }
.expand-enter-to, .expand-leave-from { opacity: 1; max-height: 800px; }

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 0 6px rgba(79,70,229,0.18); }
  50% { box-shadow: 0 0 0 12px rgba(79,70,229,0.08); }
}

/* ===== 响应式 ===== */
@media (max-width: 920px) {
  .tree-section { grid-template-columns: 1fr; }
  .fork-point span { display: none; }
}
@media (max-width: 600px) {
  .topbar { flex-wrap: wrap; }
  .nav-links { order: 3; width: 100%; justify-content: center; }
  .branch-head { flex-wrap: wrap; }
}
</style>
