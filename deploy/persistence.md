# 线上持久化存储说明

理发预约系统的**全部业务数据**（用户、预约、排班、消息、系统配置）都在数据库里。  
**线上（Vercel）必须使用 Neon PostgreSQL**，不能使用 SQLite 文件。

## 容量（Neon 免费档）

| 项 | 额度 | 对本系统的含义 |
|----|------|----------------|
| Postgres 存储 | **1 GB / 项目**（账号下免费项目合计最多 20 GB） | 实际数据通常不足 50 MB，余量很大 |
| 计算 | 100 CU·小时 / 月 / 项目 | 内部预约系统一般够用 |

官方限额见 [Neon Plans](https://neon.com/docs/introduction/plans)。

## 是否持久

| 环境 | 存储 | 持久 |
|------|------|------|
| 本地 `back/zmhair.db` | SQLite 文件 | 是（请备份文件） |
| Vercel 未配库 | 无 | **否**（启动会报错） |
| **Vercel + Neon** | 云端 Postgres | **是** |

访问 `https://你的域名/health`：

```json
"storage": {
  "engine": "postgresql",
  "persistent": true
}
```

`persistent` 必须为 **true**。

---

## 上线步骤（Neon）

**按 [neon-quickstart.md](./neon-quickstart.md) 逐步操作即可**（建 Neon 项目 → Vercel 填 `DATABASE_URL` + `SECRET_KEY` → `vercel --prod` → 看 `/health`）。

首次部署会自动建表并 seed（`admin` / `admin123`、理发师、`employees_seed.json` 员工）。

---

## 从本地 SQLite 迁到 Neon

线上是空库、只要种子数据：**不必迁移**。

本地 `back/zmhair.db` 有真实预约时：

```bash
cd back
export DATABASE_URL='postgresql://...?sslmode=require'
./venv/bin/python scripts/migrate_sqlite_to_postgres.py
```

---

## 环境变量

| 变量 | 说明 |
|------|------|
| `DATABASE_URL` | Neon 连接串（**必填**） |
| `SECRET_KEY` | JWT 密钥（**必填**，生产必改） |

`POSTGRES_URL` 仅在使用 Vercel 自带 Postgres 集成时需要；本项目默认 **Neon + DATABASE_URL**。

---

## 其它 Postgres 提供商（可选）

Supabase、自建 Postgres 等，只要连接串写入 `DATABASE_URL` 即可；**未选用 Turso**（需另改驱动，与当前代码不一致）。

部署总览见 [vercel.md](./vercel.md)。
