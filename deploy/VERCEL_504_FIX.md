# Vercel 仍 504 时按此做

## 1. 环境变量（必做）

`DATABASE_URL` 末尾 **不要** `channel_binding=require`。

Neon 可试 **Direct** 连接串（非 pooler），有时 pooler 在 Serverless 下更慢。

## 2. 推送最新代码（必做）

日志里 `/health` 仍走旧 FastAPI 时，说明 **GitHub 上还没有** `api/health.py` 和新 `main.py`。

```bash
cd /Users/Zhou/w/work/code/zmHairV
git add back/main.py back/app/bootstrap.py back/app/database.py back/app/init_data.py api/health.py vercel.json
git status
git commit -m "fix: Vercel timeout lazy bootstrap and light health"
git push origin main
```

等 Deployments **Ready** 后再测。

## 3. 验证

- `https://zmhair.vercel.app/health` → 应 **1 秒内** 返回 JSON（独立轻量函数）
- `/admin/login` → admin / admin123 应能进
- 工号 **094192** 等员工：Vercel **不会** 自动导入 3000 人，需本机执行一次：

```bash
cd back
export DATABASE_URL='你的Neon连接串（无 channel_binding）'
./venv/bin/python scripts/migrate_sqlite_to_postgres.py
```

或从 Neon SQL 手工插入测试用户。

## 4. 日志含义

`Task timed out after 30 seconds` = 函数启动或连库超过 30 秒。  
新代码：**/health 不再加载 FastAPI**；API 首次请求才轻量建表，不导全量员工。
