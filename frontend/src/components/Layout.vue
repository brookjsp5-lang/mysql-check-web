<template>
  <el-container class="layout-container">
    <!-- 左侧侧边栏 -->
    <el-aside width="200px" class="layout-aside">
      <div class="logo-area">
        <el-icon :size="24" color="#409EFF"><Monitor /></el-icon>
        <span class="logo-text">MySQL巡检</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="aside-menu"
        background-color="#1d1e1f"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/inspection">
          <el-icon><Search /></el-icon>
          <span>巡检管理</span>
        </el-menu-item>
        <el-menu-item index="/database">
          <el-icon><Coin /></el-icon>
          <span>数据库管理</span>
        </el-menu-item>
        <el-menu-item index="/report">
          <el-icon><Document /></el-icon>
          <span>报告中心</span>
        </el-menu-item>
        <el-menu-item index="/tutorial">
          <el-icon><Reading /></el-icon>
          <span>使用教程</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部栏 -->
      <el-header class="layout-header">
        <div class="header-left">
          <span class="header-title">MySQL巡检平台</span>
        </div>
        <div class="header-right">
          <el-icon><Clock /></el-icon>
          <span class="current-time">{{ currentTime }}</span>
        </div>
      </el-header>

      <!-- 主内容区域 -->
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const currentTime = ref('')
let timer = null

const activeMenu = computed(() => {
  return route.path
})

function updateTime() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  currentTime.value = `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`
}

onMounted(() => {
  updateTime()
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
  width: 100%;
}

.layout-aside {
  background-color: #1d1e1f;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.logo-area {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-bottom: 1px solid #333;
}

.logo-text {
  color: #fff;
  font-size: 16px;
  font-weight: 600;
}

.aside-menu {
  border-right: none;
  flex: 1;
}

.aside-menu .el-menu-item {
  height: 50px;
  line-height: 50px;
}

.aside-menu .el-menu-item.is-active {
  background-color: #262728 !important;
}

.layout-header {
  height: 60px;
  background-color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  z-index: 1;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #909399;
  font-size: 14px;
}

.current-time {
  font-variant-numeric: tabular-nums;
}

.layout-main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>