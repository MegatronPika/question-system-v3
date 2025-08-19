# 🔄 Railway数据备份完整指南

## 方法1：Railway CLI备份（推荐）

### 步骤1：安装Railway CLI

**macOS:**
```bash
brew install railway
```

**Linux:**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

**Windows:**
```bash
npm install -g @railway/cli
```

### 步骤2：登录Railway
```bash
railway login
```

### 步骤3：下载数据文件
```bash
# 列出项目
railway projects

# 选择项目（如果需要）
railway link

# 下载user_data.json
railway download user_data.json
```

## 方法2：Railway控制台手动备份

### 步骤1：访问Railway控制台
1. 打开 https://railway.app
2. 登录您的账户
3. 选择您的项目

### 步骤2：找到部署文件
1. 点击 "Deployments" 标签
2. 选择最新的部署
3. 在 "Files" 部分找到 `user_data.json`
4. 点击下载按钮

### 步骤3：保存备份
1. 将下载的文件重命名为：`user_data_backup_YYYYMMDD_HHMMSS.json`
2. 保存到安全位置

## 方法3：API备份（需要先部署更新）

### 步骤1：部署包含备份API的代码
```bash
git add .
git commit -m "Add backup API endpoint"
git push
```

### 步骤2：使用API下载数据
```bash
curl -H "X-Backup-Key: question_bank_backup_2025" \
     https://your-app.railway.app/api/backup \
     -o user_data_backup.json
```

## 方法4：使用备份脚本

### 运行自动备份脚本
```bash
python railway_backup.py
```

选择相应的备份方式即可。

## 验证备份

### 检查备份文件
```bash
# 查看文件大小
ls -lh user_data_backup_*.json

# 验证JSON格式
python -m json.tool user_data_backup_*.json > /dev/null && echo "✅ JSON格式正确" || echo "❌ JSON格式错误"

# 查看用户数量
python -c "
import json
with open('user_data_backup_*.json') as f:
    data = json.load(f)
    if 'data' in data:
        data = data['data']
    print(f'用户数量: {len(data.get(\"user_profiles\", {}))}')
"
```

## 恢复数据

### 方法1：通过Railway CLI
```bash
# 上传备份文件
railway upload user_data_backup_YYYYMMDD_HHMMSS.json user_data.json
```

### 方法2：通过控制台
1. 在Railway控制台中
2. 进入项目设置
3. 上传备份文件
4. 重命名为 `user_data.json`

## 安全注意事项

### ✅ 备份最佳实践
- 定期备份（建议每天）
- 保存多个备份版本
- 验证备份文件完整性
- 存储在安全位置

### ⚠️ 安全警告
- 备份文件包含敏感用户数据
- 不要将备份文件提交到Git
- 使用安全的传输方式
- 定期清理旧备份

## 故障排除

### 常见问题

**Q: Railway CLI安装失败**
A: 尝试手动安装：https://docs.railway.app/develop/cli

**Q: 无法下载文件**
A: 检查项目权限和登录状态

**Q: 备份文件损坏**
A: 尝试重新下载或使用其他方法

**Q: API备份失败**
A: 确认应用已部署最新代码

### 联系支持
如果遇到问题，可以：
1. 查看Railway文档：https://docs.railway.app
2. 联系Railway支持
3. 使用备用备份方法

## 自动化备份

### 设置定时备份
```bash
# 创建定时任务（Linux/macOS）
crontab -e

# 添加以下行（每天凌晨2点备份）
0 2 * * * cd /path/to/project && python railway_backup.py
```

### 使用GitHub Actions
创建 `.github/workflows/backup.yml`:
```yaml
name: Daily Backup
on:
  schedule:
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  backup:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install Railway CLI
        run: npm install -g @railway/cli
      - name: Backup Data
        run: |
          railway login --token ${{ secrets.RAILWAY_TOKEN }}
          railway download user_data.json
          # 处理备份文件...
``` 