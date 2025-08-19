# 金融业数字化转型技能大赛题库系统

## 项目简介

基于 Flask 的在线题库系统，支持多用户、多题型练习、模拟考试、错题与重点题管理，提供“全量题库/重点题库/错题记录”统一入口与高性能分页加载。

## 主要功能

- 多用户：注册/登录、个人数据隔离
- 随机练习：全量/未做/错题/重点题（含题型筛选）
- 模拟考试：按题型顺序出题（单选→判断→多选），支持断点续考与超时自动结算
- 全量题库：分题型独立分页、状态筛选（未做/做对/错题/常错/重点）、编号图标与详情弹窗
- 重点题库：统一“标记为重点/取消重点”按钮（全站一致）
- 错题记录：做错次数准确统计与排序
- 性能优化：题库缓存（pickle）、后端分页、前端按需加载

## 技术栈

- 后端：Flask (Python)
- 前端：Bootstrap 5 + jQuery
- 存储：Postgres（优先，可选）+ Railway 持久化卷文件作为兜底
- 认证：Flask Session + Werkzeug

## 本地运行

1) 安装依赖
```bash
pip install -r requirements.txt
```

2) 启动
```bash
python run.py
```

3) 访问
- 本地：http://localhost:8080

## 部署（Railway）

1) 配置 `railway.toml`（已提供）并连接仓库部署。
2) 开启持久化卷，默认使用 `/data`。
3) 可选开启 Postgres，并在服务环境变量中设置：
- `DATABASE_URL`= 你的 Postgres 连接串（Railway 创建后自动注入或手动添加）

启动命令默认使用 `python run.py`。

## 数据持久化

系统的数据读写优先级：
1) **Postgres**（`DATABASE_URL` 存在时启用，表：`kv_store(key TEXT PRIMARY KEY, value TEXT)`，键：`user_data`）
2) **Railway 持久化卷文件**：`/data/user_data.json`
3) **本地文件**：`user_data.json`

### 数据流机制

**读取时**：
- 优先从数据库读取（权威数据源）
- 数据库有数据时，自动同步到本地文件（Railway环境）
- 数据库无数据时，从文件/环境变量回填到数据库

**保存时**：
- 优先保存到数据库
- Railway环境：同时保存到持久化卷作为备份
- 本地环境：同时保存到本地文件

**数据一致性**：
- 数据库是权威数据源，重启后数据不会丢失
- 文件主要用于备份和初始化
- 支持手动数据同步：`POST /admin/sync_data`（需要 `X-Admin-Token: sync_2024`）

### 备份与恢复

- 紧急备份脚本：`python emergency_data_recovery.py`
- 卷文件备份：下载 `/data/user_data.json`
- API 备份（部署后）：
```bash
curl -H "X-Backup-Key: question_bank_backup_2025" \
     https://your-app.railway.app/api/backup \
     -o user_data_backup.json
```

- 手动数据同步：
```bash
curl -X POST -H "X-Admin-Token: sync_2024" \
     https://your-app.railway.app/admin/sync_data
```

## 安全更新与运维

- 更新前务必备份（卷文件/DB 备份/API 备份任一种）
- 低峰期发布；更新后自检主要功能与数据完整性
- 出现异常可回滚代码并用备份恢复数据

## 项目结构

```
new/
├── app.py                 # Flask 应用
├── run.py                 # 启动脚本
├── requirements.txt       # 依赖（含 psycopg2-binary）
├── full_questions.json    # 题库数据
├── templates/             # 页面模板
├── static/                # 静态资源
└── *.md / 脚本            # 文档与备份脚本
```

## 变更与修复（节选）

- 错题次数统计修复：按错题记录真实出现次数统计
- 未做题去重：抽题即记“已做”防重复
- 考试多选修复：多选使用复选框+数组答案
- 考试题序：单选→判断→多选
- 全量题库：状态筛选（含“常错/重点”）、分题型分页、编号图标
- 重点题：全站统一“标记/取消”按钮
- 断点续考：开始考试自动恢复未完成场次，离开页面保存进度，超时自动结算
- 数据持久化：新增 Postgres 优先+卷文件兜底

## 许可证

MIT License# question-system-v4
