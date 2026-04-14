<template>
  <div class="dashboard-container">
    <!-- 顶部统计卡片 -->
    <el-row :gutter="20" class="stat-row">
      <el-col :span="6">
        <StatCard
          title="数据库总数"
          :value="stats.total_databases"
          icon="Coin"
          color="#409EFF"
        />
      </el-col>
      <el-col :span="6">
        <StatCard
          title="巡检总次数"
          :value="stats.total_inspections"
          icon="Search"
          color="#67C23A"
        />
      </el-col>
      <el-col :span="6">
        <StatCard
          title="健康实例数"
          :value="stats.healthy_instances"
          icon="CircleCheck"
          color="#67C23A"
        />
      </el-col>
      <el-col :span="6">
        <StatCard
          title="异常实例数"
          :value="stats.unhealthy_instances"
          icon="WarningFilled"
          color="#F56C6C"
        />
      </el-col>
    </el-row>

    <!-- 下方内容区 -->
    <el-row :gutter="20" class="content-row">
      <!-- 左侧：最近巡检记录 -->
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header>
            <div class="card-header">
              <span>最近巡检记录</span>
              <el-button text type="primary" @click="$router.push('/inspection')">
                查看全部
              </el-button>
            </div>
          </template>
          <el-table :data="recentInspections" v-loading="loading" stripe size="small" max-height="400">
            <el-table-column prop="id" label="ID" width="60" />
            <el-table-column prop="database_name" label="数据库名称" min-width="120" />
            <el-table-column prop="host" label="服务器地址" min-width="140" />
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)" size="small">
                  {{ getStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="健康状态" width="100">
              <template #default="{ row }">
                <HealthBadge v-if="row.health_status" :status="row.health_status" />
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column prop="problem_count" label="问题数" width="80" align="center">
              <template #default="{ row }">
                <span :style="{ color: row.problem_count > 0 ? '#F56C6C' : '#67C23A' }">
                  {{ row.problem_count ?? '-' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="started_at" label="开始时间" min-width="160">
              <template #default="{ row }">
                {{ formatTime(row.started_at) }}
              </template>
            </el-table-column>
          </el-table>
          <el-empty v-if="!loading && recentInspections.length === 0" description="暂无巡检记录" />
        </el-card>
      </el-col>

      <!-- 右侧：健康状态分布 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header>
            <span>健康状态分布</span>
          </template>
          <div class="chart-container" v-loading="loading">
            <el-empty v-if="!loading && !healthDistribution" description="暂无数据" />
            <div v-if="healthDistribution" class="pie-chart">
              <div class="pie-chart-visual">
                <div
                  class="pie-segment"
                  v-for="(item, index) in pieSegments"
                  :key="index"
                  :style="{
                    backgroundColor: item.color,
                    width: item.percent + '%'
                  }"
                  :title="item.label + ': ' + item.value"
                />
              </div>
              <div class="pie-legend">
                <div
                  v-for="(item, index) in legendItems"
                  :key="index"
                  class="legend-item"
                >
                  <span class="legend-dot" :style="{ backgroundColor: item.color }"></span>
                  <span class="legend-label">{{ item.label }}</span>
                  <span class="legend-value">{{ item.value }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getDashboardStats, getInspections } from '../api/index'
import StatCard from '../components/StatCard.vue'
import HealthBadge from '../components/HealthBadge.vue'

const loading = ref(false)
const stats = ref({
  total_databases: 0,
  total_inspections: 0,
  healthy_instances: 0,
  unhealthy_instances: 0
})
const recentInspections = ref([])
const healthDistribution = ref(null)

const statusMap = {
  pending: { type: 'info', text: '等待中' },
  running: { type: '', text: '运行中' },
  completed: { type: 'success', text: '已完成' },
  failed: { type: 'danger', text: '失败' }
}

function getStatusType(status) {
  return statusMap[status]?.type || 'info'
}

function getStatusText(status) {
  return statusMap[status]?.text || status
}

function formatTime(time) {
  if (!time) return '-'
  return time.replace('T', ' ').substring(0, 19)
}

const pieSegments = computed(() => {
  if (!healthDistribution.value) return []
  const dist = healthDistribution.value
  const total = Object.values(dist).reduce((a, b) => a + b, 0)
  if (total === 0) return []
  const colorMap = {
    '优秀': '#67C23A',
    '良好': '#409EFF',
    '一般': '#E6A23C',
    '需关注': '#F56C6C',
    'healthy': '#67C23A',
    'warning': '#E6A23C',
    'critical': '#F56C6C'
  }
  return Object.entries(dist)
    .filter(([, value]) => value > 0)
    .map(([label, value]) => ({
      label,
      value,
      percent: (value / total) * 100,
      color: colorMap[label] || '#909399'
    }))
})

const legendItems = computed(() => {
  if (!healthDistribution.value) return []
  const dist = healthDistribution.value
  const colorMap = {
    '优秀': '#67C23A',
    '良好': '#409EFF',
    '一般': '#E6A23C',
    '需关注': '#F56C6C',
    'healthy': '#67C23A',
    'warning': '#E6A23C',
    'critical': '#F56C6C'
  }
  return Object.entries(dist).map(([label, value]) => ({
    label,
    value,
    color: colorMap[label] || '#909399'
  }))
})

async function fetchData() {
  loading.value = true
  try {
    const [statsData, inspectionsData] = await Promise.all([
      getDashboardStats(),
      getInspections({ page: 1, page_size: 10 })
    ])
    stats.value = {
      total_databases: statsData.db_total || 0,
      total_inspections: statsData.inspection_total || 0,
      healthy_instances: statsData.healthy_count || 0,
      unhealthy_instances: statsData.warning_count || 0
    }
    if (statsData.health_distribution) {
      healthDistribution.value = statsData.health_distribution
    }
    recentInspections.value = inspectionsData.items || []
  } catch (e) {
    console.error('获取仪表盘数据失败:', e)
    ElMessage.error('获取仪表盘数据失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.dashboard-container {
  width: 100%;
}

.stat-row {
  margin-bottom: 20px;
}

.content-row {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.chart-container {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pie-chart {
  width: 100%;
  padding: 20px 0;
}

.pie-chart-visual {
  display: flex;
  height: 30px;
  border-radius: 15px;
  overflow: hidden;
  margin-bottom: 24px;
}

.pie-segment {
  height: 100%;
  transition: all 0.3s;
  min-width: 4px;
}

.pie-segment:hover {
  opacity: 0.8;
}

.pie-legend {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 3px;
  flex-shrink: 0;
}

.legend-label {
  color: #606266;
  flex: 1;
}

.legend-value {
  font-weight: 600;
  color: #303133;
}
</style>