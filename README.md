# 金融业数字化转型技能大赛题库系统

## 项目简介

这是一个基于Flask的在线题库练习系统，支持多用户登录、随机做题、模拟考试和错题管理功能。

## 主要功能

### 🔐 多用户系统
- 用户注册和登录
- 个人数据隔离
- 会话持久化

### 📚 题库练习
- **全量题库**：从所有题目中随机出题
- **未做题库**：从未做过的题目中随机出题  
- **错题库**：从做错的题目中随机出题
- **多选题支持**：支持多选答案的题目类型

### 📝 模拟考试
- 150道题目（50单选 + 50多选 + 50判断）
- 1小时限时
- 自动评分和错题记录

### ❌ 错题管理
- 按题型分类（单选、多选、判断）
- 多种排序方式（时间、错题次数、题目ID）
- 详细解析和正确答案显示

## 技术栈

- **后端**：Flask (Python)
- **前端**：Bootstrap 5 + jQuery
- **数据存储**：JSON文件
- **用户认证**：Flask Session + Werkzeug

## 快速开始

### 本地运行

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **启动服务**
   ```bash
   python run.py
   ```

3. **访问系统**
   - 本地访问：http://localhost:8080
   - 局域网访问：http://你的IP:8080

### 部署到Railway

1. **创建GitHub仓库**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/question-bank-system.git
   git push -u origin main
   ```

2. **Railway部署**
   - 登录Railway: https://railway.app
   - 点击 "New Project"
   - 选择 "Deploy from GitHub repo"
   - 选择您的仓库
   - 点击 "Deploy Now"

## 项目结构

```
question-bank-system/
├── app.py              # Flask主应用
├── run.py              # 启动脚本
├── requirements.txt    # Python依赖
├── full_questions.json # 题库数据
├── templates/          # HTML模板
│   ├── base.html       # 基础模板
│   ├── index.html      # 主页
│   ├── login.html      # 登录页
│   ├── register.html   # 注册页
│   ├── profile.html    # 个人资料
│   ├── random_practice.html # 随机做题
│   ├── exam.html       # 考试页面
│   └── wrong_questions.html # 错题页面
└── static/             # 静态资源
    ├── css/            # 样式文件
    └── js/             # JavaScript文件
```

## 题库信息

- **总题目数**：1468道
- **题目类型**：
  - 单选题：520道
  - 多选题：515道  
  - 判断题：433道
- **总分**：9915分

## 更新日志

### v2.0.0 (2025-08-17)
- ✅ 修复多选题答案错误问题
- ✅ 新增多用户系统
- ✅ 支持用户注册、登录、登出
- ✅ 个人数据隔离管理
- ✅ 会话持久化功能
- ✅ 个人资料页面
- ✅ 多选题多选功能

### v1.0.0 (2025-08-17)
- ✅ 基础题库系统
- ✅ 随机做题功能
- ✅ 模拟考试功能
- ✅ 错题管理功能

## 许可证

MIT License # question-system-v3
