# 部署与更新（Railway）

完整的部署与安全更新指南已合并到主文档 README：

请查看：README.md 中的“部署（Railway）/ 数据持久化 / 安全更新与运维”章节。

要点速览：
- 使用 `railway.toml` 自动启用持久化卷 `/data`；
- 可选配置 `DATABASE_URL` 启用 Postgres 持久化；
- 更新前请先备份（卷文件/DB/API 备份脚本）；
- 部署完成后验证数据与核心功能。