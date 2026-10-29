# Vercel 部署说明

将 **Vue 静态前端** 与 **FastAPI 后端** 部署在同一 Vercel 项目上：页面走 CDN，接口走 Python Serverless。

> **重要**：Vercel 无持久磁盘，**不能使用 SQLite**。线上持久化固定为 **Neon PostgreSQL** → **[neon-quickstart.md](./neon-quickstart.md)**（逐步清单）。

## 1. 准备 Neon 数据库

见 **[neon-quickstart.md](./neon-quickstart.md)** 第一步：注册 Neon、新建 Project、复制 `postgresql://…?sslmode=require` 到 Vercel 的 `DATABASE_URL`。

## 2. 部署到 Vercel

```bash
cd /path/to/zmHairV
npm i -g vercel   # 未安装时
vercel login
vercel            # 首次：Link 项目、Root Directory 选仓库根目录 zmHairV
vercel --prod
```

或在 [vercel.com](https://vercel.com) 导入 Git 仓库，**Root Directory** 设为 `zmHairV`（若 monorepo 则在子目录）。

## 3. 环境变量（Vercel → Settings → Environment Variables）

| 变量 | 说明 | 示例 |
|------|------|------|
| `DATABASE_URL` | **必填**（生产持久化） | `postgresql://...` |
| `POSTGRES_URL` | Vercel Postgres 集成时自动注入 | 可不手工填 |
| `SECRET_KEY` | JWT 密钥，务必随机长串 | 自行生成 |
| `APP_NAME` | 可选 | 企业内部理发预约系统 |
| `JWT_EXPIRE_HOURS` | 可选 | `72` |

`VERCEL` 由平台自动注入，用于关闭 SQLite、使用 `NullPool` 等。

## 4. 访问地址

| 入口 | 路径 |
|------|------|
| 移动端 H5 | `https://你的域名/m/login` |
| PC 管理后台 | `https://你的域名/admin/login` |
| 健康检查 | `https://你的域名/health` |
| API 文档 | `https://你的域名/docs` |

前端 axios 使用相对路径 `/api`，无需改代码。

## 5. 路由说明（vercel.json）

- `/api/*`、`/health`、`/docs`、`/openapi.json` → `api/index.py`（FastAPI）
- 静态资源 → `front/dist`
- 其余路径 → `index.html`（Vue History 模式）

## 6. 本地开发（不变）

```bash
cd back && ./start.sh          # API :8001
cd front && ./start.sh         # 或 npm run serve :8080
```

本地仍用 `sqlite:///./zmhair.db`。

## 7. 本地模拟 Vercel（可选）

```bash
vercel dev
```

需在本机 `.env` 或 shell 中配置 `DATABASE_URL`（PostgreSQL）才能与线上一致。

## 8. 常见问题

**部署后 500 / 启动失败**  
- 检查是否未设置 `DATABASE_URL` 仍用 SQLite（Vercel 会拒绝启动）。  
- 查看 Vercel → Deployments → Functions 日志。

**冷启动较慢**  
- Serverless 首次访问会初始化数据库表与种子数据，属正常现象。

**内网域名**  
- Vercel 默认为公网 HTTPS；若必须内网，请继续用 `deploy/部署说明.md` 的 IIS/Nginx 方案。
