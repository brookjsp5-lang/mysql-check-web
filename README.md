# MySQL 巡检平台 (Web版)

基于 [MySQLDBCHECK](https://github.com) 命令行巡检工具重构的 Web 版 MySQL 数据库健康巡检平台。

## 架构概览

```
┌─────────────────────────────────────────────────┐
│              Vue3 + Element Plus 前端              │
│  ┌──────────┐ ┌──────────┐ ┌────────┐ ┌───────┐ │
│  │  仪表盘   │ │ 巡检管理  │ │数据库管理│ │报告中心│ │
│  └──────────┘ └──────────┘ └────────┘ └───────┘ │
└────────────────────┬────────────────────────────┘
                     │ HTTP (REST API)
┌────────────────────▼────────────────────────────┐
│              FastAPI 后端                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ 巡检引擎  │ │ 风险分析  │ │  Word报告生成     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │MySQL采集  │ │系统采集   │ │  SQLite持久化     │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
└─────────────────────────────────────────────────┘
```

## 功能特性

- **40+ 项 MySQL 巡检**：覆盖基础信息、连接配置、内存配置、InnoDB引擎、性能分析、日志复制、安全信息等
- **系统资源监控**：支持本地(psutil)和SSH远程(paramiko)两种方式采集CPU、内存、磁盘信息
- **智能风险分析**：12类自动检查规则，自动计算健康评分(0-100)
- **Word 报告生成**：一键生成结构化的健康巡检报告
- **数据库配置管理**：支持添加、编辑、删除、测试连接
- **批量巡检**：支持同时对多个数据库实例执行巡检
- **历史记录**：所有巡检结果持久化存储，支持趋势分析
- **异步执行**：巡检任务后台执行，不阻塞界面操作

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue3 + Vue Router + Axios + Element Plus |
| 后端 | FastAPI + SQLAlchemy + aiosqlite |
| 采集 | pymysql + paramiko + psutil |
| 报告 | python-docx |
| 部署 | Docker + Docker Compose + Nginx |

## 快速开始

### 方式一：Docker Compose 部署（推荐）

```bash
# 1. 克隆项目
cd mysql-check-web

# 2. 一键启动
docker-compose up -d --build

# 3. 访问应用
# 前端：http://localhost:5173
# API文档：http://localhost:8000/docs
```

### 方式二：手动启动

#### 后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### 前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:5173

## 项目结构

```
mysql-check-web/
├── docker-compose.yml          # Docker编排
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── reports/                # Word报告输出目录
│   ├── data/                   # SQLite数据库目录
│   └── app/
│       ├── main.py             # FastAPI入口
│       ├── config.py           # 配置管理
│       ├── database.py         # 数据库模型
│       ├── models.py           # Pydantic模型
│       ├── collectors/         # 数据采集器
│       │   ├── mysql_collector.py
│       │   ├── system_local.py
│       │   └── system_remote.py
│       ├── services/           # 业务服务
│       │   ├── inspection_service.py
│       │   ├── report_service.py
│       │   └── risk_analyzer.py
│       └── routers/            # API路由
│           ├── inspection.py
│           ├── database.py
│           └── report.py
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── router/
        ├── api/
        ├── views/              # 4个页面
        └── components/         # 公共组件
```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/databases | 添加数据库配置 |
| GET | /api/databases | 获取数据库列表 |
| PUT | /api/databases/{id} | 更新数据库配置 |
| DELETE | /api/databases/{id} | 删除数据库 |
| POST | /api/databases/{id}/test | 测试MySQL连接 |
| POST | /api/inspections | 创建巡检任务 |
| GET | /api/inspections | 获取巡检列表 |
| GET | /api/inspections/{id} | 获取巡检详情 |
| GET | /api/inspections/{id}/status | 查询巡检状态 |
| POST | /api/inspections/{id}/cancel | 取消巡检 |
| POST | /api/inspections/batch | 批量巡检 |
| GET | /api/reports | 获取报告列表 |
| GET | /api/reports/{id}/download | 下载Word报告 |
| GET | /api/reports/detail/{id} | 获取巡检详细结果 |

完整API文档启动后访问：http://localhost:8000/docs

## 巡检项清单

| 类别 | 巡检项 |
|------|--------|
| 基础信息 | MySQL版本、实例启动时间、服务器平台、安装路径 |
| 连接配置 | 当前/最大/历史最大连接数、侦听队列、交互超时、文件打开限制、域名解析 |
| 内存配置 | InnoDB缓冲池、排序/连接缓冲区、线程缓存、最大包大小 |
| InnoDB引擎 | I/O容量、独立表空间、打开文件数、并发线程、日志刷新策略、Binlog同步 |
| 性能分析 | QPS查询总数、锁信息(立即/等待)、异常连接、当前进程列表 |
| 日志复制 | 慢查询日志、Binlog状态/保留天数、查询缓存、主从复制状态 |
| 数据库信息 | 各库大小(数据/索引)、数据库用户列表 |
| 系统资源 | CPU使用率/核心数、内存使用率、磁盘分区使用率 |
| 风险分析 | 连接数使用率、缓冲池大小、内存/磁盘使用率等12类规则 |

## 与原项目对比

| 特性 | 原版 (MySQLDBCHECK) | Web版 (本项目) |
|------|---------------------|---------------|
| 交互方式 | 命令行交互 | Web界面 |
| 架构 | 单文件2000行 | 模块化分层架构 |
| 数据持久化 | 无 | SQLite |
| 批量巡检 | Excel导入 | Web界面多选 |
| 报告格式 | Word | Word + 在线预览 |
| 系统信息 | 本地/SSH | 本地/SSH |
| 部署方式 | PyInstaller打包 | Docker Compose |
| API接口 | 无 | 16个REST API |
| 密码存储 | 明文 | Fernet加密 |
| 风险规则 | 4条 | 12条 |

## License

MIT