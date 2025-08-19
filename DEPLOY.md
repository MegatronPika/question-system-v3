# 🔄 安全更新指南

## ⚠️ 重要提醒

**Railway的文件系统是临时的！** 每次重新部署都会丢失数据。我们已经实现了数据持久化解决方案，但更新前仍需要备份。

## 数据持久化解决方案

### 1. 持久化存储配置
- 使用Railway的持久化卷（`/data`目录）
- 环境变量备份
- 多重备份机制

### 2. 数据存储位置优先级
1. `/data/user_data.json` - 持久化卷（推荐）
2. `USER_DATA_JSON` 环境变量
3. `user_data.json` - 本地文件

## 更新前准备

### 1. 紧急备份当前数据

**方法1：使用紧急备份脚本**
```bash
python emergency_data_recovery.py
# 选择选项2：创建紧急备份
```

**方法2：通过Railway控制台**
1. 登录 https://railway.app
2. 选择您的项目
3. 进入 "Deployments" → 最新部署 → "Files"
4. 下载 `user_data.json` 或 `/data/user_data.json`

**方法3：使用Railway CLI**
```bash
railway login
railway download user_data.json
# 或
railway download /data/user_data.json
```

### 2. 验证备份
```bash
python emergency_data_recovery.py
# 选择选项1：检查当前数据状态
```

## 更新步骤

### 方法1：GitHub自动部署（推荐）

1. **提交更新到GitHub**
   ```bash
   git add .
   git commit -m "Fix: 添加数据持久化支持"
   git push
   ```

2. **Railway自动重新部署**
   - Railway会检测到GitHub仓库更新
   - 自动触发重新部署
   - 数据会自动从持久化存储恢复

3. **验证数据恢复**
   ```bash
   # 检查应用是否正常运行
   curl https://your-app.railway.app
   
   # 检查数据是否恢复
   python emergency_data_recovery.py
   ```

### 方法2：手动更新（如果需要）

1. **在Railway控制台中**
   - 进入项目设置
   - 找到"Variables"标签
   - 添加环境变量：`MAINTENANCE_MODE=true`

2. **更新代码**
   - 上传新的文件
   - 确保包含数据持久化功能

3. **恢复用户数据**
   ```bash
   python emergency_data_recovery.py
   # 选择选项4：从备份恢复数据
   ```

4. **关闭维护模式**
   - 删除环境变量：`MAINTENANCE_MODE`

## 验证更新

### 1. 检查数据持久化
```bash
# 测试数据持久化
python railway_persistent_storage.py
# 选择选项5：测试数据持久化
```

### 2. 检查应用功能
- 访问登录页面
- 验证用户数据是否完整
- 测试多选题功能
- 检查个人资料页面

### 3. 检查API接口
```bash
# 测试用户统计接口
curl -X POST https://your-app.railway.app/get_user_stats \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 回滚方案

如果更新出现问题：

1. **立即回滚代码**
   ```bash
   git revert HEAD
   git push
   ```

2. **恢复用户数据**
   ```bash
   python emergency_data_recovery.py
   # 选择选项4：从备份恢复数据
   ```

3. **检查数据完整性**
   ```bash
   python emergency_data_recovery.py
   # 选择选项1：检查当前数据状态
   ```

## 数据管理工具

### 1. 紧急数据恢复工具
```bash
python emergency_data_recovery.py
```
- 检查数据状态
- 创建紧急备份
- 从备份恢复
- 创建测试数据

### 2. Railway持久化存储管理
```bash
python railway_persistent_storage.py
```
- 设置持久化卷
- 管理备份文件
- 测试数据持久化

### 3. Railway备份工具
```bash
python railway_backup.py
```
- Railway CLI备份
- API备份
- 手动备份指南

## 注意事项

### ✅ 安全措施
- 更新前必须备份用户数据
- 使用Git版本控制
- 保留回滚方案
- 在低峰期进行更新
- 启用数据持久化

### ⚠️ 风险提示
- Railway文件系统是临时的
- 不要直接修改生产环境的文件
- 不要删除现有的用户数据
- 确保新代码向后兼容
- 测试数据持久化功能

### 📋 检查清单
- [ ] 备份用户数据
- [ ] 测试新功能
- [ ] 提交到GitHub
- [ ] 验证Railway部署
- [ ] 测试生产环境
- [ ] 确认用户数据完整
- [ ] 验证数据持久化

## 紧急联系

如果遇到问题：
1. 立即回滚到上一个版本
2. 恢复用户数据备份
3. 检查错误日志
4. 联系技术支持

## 配置文件说明

### railway.toml
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python run.py"
healthcheckPath = "/"
healthcheckTimeout = 300
restartPolicyType = "on_failure"

[[services]]
name = "question-bank-system"
port = 8080

# 启用持久化存储
[services.volumes]
data = "/data"

# 环境变量配置
[services.variables]
RAILWAY_ENVIRONMENT = "true"
USER_DATA_FILE = "/data/user_data.json"
```

这个配置文件确保：
- 使用持久化卷存储数据
- 设置正确的环境变量
- 配置健康检查
- 设置重启策略 