import { createRouter, createWebHistory } from 'vue-router'
import Layout from '../components/Layout.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('../views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'inspection',
        name: 'Inspection',
        component: () => import('../views/Inspection.vue'),
        meta: { title: '巡检管理' }
      },
      {
        path: 'database',
        name: 'Database',
        component: () => import('../views/Database.vue'),
        meta: { title: '数据库管理' }
      },
      {
        path: 'report',
        name: 'Report',
        component: () => import('../views/Report.vue'),
        meta: { title: '报告中心' }
      },
      {
        path: 'tutorial',
        name: 'Tutorial',
        component: () => import('../views/Tutorial.vue'),
        meta: { title: '使用教程' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router