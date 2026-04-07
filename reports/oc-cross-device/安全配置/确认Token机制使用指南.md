# 确认 Token 机制使用指南（v1.1.0）

## 什么是确认 Token

确认 Token（Confirm Token）是用于**敏感操作的二次确认**的安全机制。

当用户执行危险操作（如删除模板、撤销 Key）时，系统会：
1. 生成一个 6 位 Token（有效期 5 分钟）
2. 向用户推送确认卡片
3. 用户确认后，操作才会真正执行

## 已接入确认 Token 的操作

| 操作 | 触发条件 |
|------|----------|
| 删除模板 | `DELETE /api/v1/templates/{id}` |
| 删除定时任务 | `DELETE /api/v1/scheduler/jobs/{id}` |
| 撤销 API Key | `DELETE /api/v1/keys/{id}` |
| 创建 API Key | `POST /api/v1/keys` |

## API 使用流程

### Step 1：请求确认 Token

```bash
curl -X POST http://localhost:8081/api/v1/confirm/request \
  -H "Authorization: Bearer sk-xxxxx-EXECUTE" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "template_delete",
    "resource_id": "daily_brief",
    "channel": "dingtalk",
    "extra": {"template_name": "daily_brief"}
  }'
```

**响应**：
```json
{
  "success": true,
  "token": "A3F7B2",
  "expires_at": "2026-03-29T12:35:00",
  "message": "确认请求已发送到 dingtalk，请在 5 分钟内确认"
}
```

### Step 2：查看确认卡片

系统会向指定渠道（钉钉/Telegram）发送确认卡片：

```
⚠️ 确认删除模板

操作类型：template_delete
模板：**daily_brief**
发起人：admin_key
来源IP：192.168.1.100
Token：A3F7B2
有效期：5 分钟内有效

⚠️ 此操作不可逆，请确认是否继续
```

### Step 3：验证 Token（用户确认后）

```bash
curl -X POST http://localhost:8081/api/v1/confirm/verify \
  -H "Authorization: Bearer sk-xxxxx-EXECUTE" \
  -H "Content-Type: application/json" \
  -d '{"token": "A3F7B2"}'
```

**响应**：
```json
{
  "success": true,
  "action": "template_delete",
  "resource_id": "daily_brief",
  "extra": {"template_name": "daily_brief"}
}
```

返回 `success=true` 后，执行实际危险操作。

### Step 4：执行实际操作

携带 Token 验证结果，执行真正的删除操作：
```bash
curl -X DELETE http://localhost:8081/api/v1/templates/daily_brief \
  -H "Authorization: Bearer sk-xxxxx-ADMIN"
```

## Web Admin 集成

Web Admin 已内置确认 Token 流程：
- 删除模板/Key 时自动弹出确认对话框
- 用户确认后自动完成删除
- Token 通过钉钉卡片推送

## 高级配置

```bash
# Token 有效期（分钟，默认 5）
export CONFIRM_TOKEN_TTL=5

# 最大待确认数（默认 50）
export CONFIRM_MAX_PENDING=50
```

## 审计日志

所有确认请求和验证都会记录到审计日志：

```bash
curl http://localhost:8081/api/v1/audit \
  -H "Authorization: Bearer sk-xxxxx-ADMIN"
```

记录的操作类型：
- `confirm_request` — 发起确认请求
- `confirm_verify` — Token 验证通过
- `confirm_expired` — Token 已过期（系统清理时）
