# 🔄 安全更新指南

## 更新前准备

### 1. 备份当前数据
在Railway控制台中，下载当前的`user_data.json`文件：

```bash
# 在本地项目目录中
python backup_user_data.py backup
```

### 2. 验证备份
```bash
python backup_user_data.py list
```

## 更新步骤

### 方法1：GitHub自动部署（推荐）

1. **提交更新到GitHub**
   ```bash
   git add .
   git commit -m "Fix: 添加用户统计API接口"
   git push
   ```

2. **Railway自动重新部署**
   - Railway会检测到GitHub仓库更新
   - 自动触发重新部署
   - 部署完成后，用户数据会自动恢复

### 方法2：手动更新（如果需要）

1. **在Railway控制台中**
   - 进入项目设置
   - 找到"Variables"标签
   - 添加环境变量：`MAINTENANCE_MODE=true`

2. **更新代码**
   - 上传新的`app.py`文件
   - 确保包含新的API接口

3. **恢复用户数据**
   ```bash
   python backup_user_data.py restore user_data_backup_YYYYMMDD_HHMMSS.json
   ```

4. **关闭维护模式**
   - 删除环境变量：`MAINTENANCE_MODE`

## 验证更新

### 1. 检查API接口
```bash
# 测试用户统计接口
curl -X POST https://your-app.railway.app/get_user_stats \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 2. 检查个人资料页面
- 访问个人资料页面
- 确认学习统计数据正常显示
- 确认考试记录正常显示

## 回滚方案

如果更新出现问题：

1. **立即回滚代码**
   ```bash
   git revert HEAD
   git push
   ```

2. **恢复用户数据**
   ```bash
   python backup_user_data.py restore user_data_backup_YYYYMMDD_HHMMSS.json
   ```

## 注意事项

### ✅ 安全措施
- 更新前必须备份用户数据
- 使用Git版本控制
- 保留回滚方案
- 在低峰期进行更新

### ⚠️ 风险提示
- 不要直接修改生产环境的文件
- 不要删除现有的用户数据
- 确保新代码向后兼容

### 📋 检查清单
- [ ] 备份用户数据
- [ ] 测试新功能
- [ ] 提交到GitHub
- [ ] 验证Railway部署
- [ ] 测试生产环境
- [ ] 确认用户数据完整

## 紧急联系

如果遇到问题：
1. 立即回滚到上一个版本
2. 恢复用户数据备份
3. 检查错误日志
4. 联系技术支持 