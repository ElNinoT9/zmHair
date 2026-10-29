# Neon + Vercel 上线清单（推荐方案）

线上持久化采用 **[Neon](https://neon.tech)** 免费档 PostgreSQL：**1 GB/项目**（理发系统实际只占几 MB～几十 MB，足够用）。

## 第一步：Neon 建库并复制连接串

1. 打开 https://neon.tech 注册并登录。
2. **New Project** → 选区域（你截图里是 **AWS US East 2** 也可以先用）。
3. 进入项目后，在 **Branch overview** 页面（左侧当前是 **Overview**）：
   - 看左侧边栏**最上方、项目名称下面**，有一行绿色按钮 **「Connect」**（不是 Settings 里的文字）。
   - 点击 **Connect**，会弹出连接信息窗口。
4. 在弹窗里：
   - **Branch** 选 `production`（默认分支即可）。
   - **Connection type** 选 **Pooled connection**（连 Vercel Serverless 建议用这个；若没有 Pooled，用 **Direct** 也行）。
   - 找到 **Connection string** 一行，点右侧 **Copy**（或显示为 `postgresql://…` / `postgres://…` 整段复制）。
5. 连接串形如：  
   `postgresql://用户名:密码@ep-xxxx.us-east-2.aws.neon.tech/neondb?sslmode=require`  
   密码里若有特殊字符，Neon 复制出来一般是 URL 编码好的，**整段原样**贴到 Vercel 即可。

> **找不到 “Connection details”？** 新版 Neon 已改成左侧 **Connect** 按钮，不再单独叫 Connection details。  
> 备选：左侧 **Settings** → 有时会有 **Connection string**；或点表格里 **Postgres database** 那一行右侧的 **Connect / 连接** 入口，效果相同。

## 第二步：把连接串填进 Vercel（不是 Neon 里找）

Neon 上复制好连接串后，打开 **Vercel**（vercel.com）→ 你的 **zmHair** 项目 → **Settings** → **Environment Variables**：

| Name | Value |
|------|--------|
| `DATABASE_URL` | 上一步 Neon 连接串 |
| `SECRET_KEY` | 自行生成一长串随机字符（勿用默认值） |

可选：`APP_NAME`、`JWT_EXPIRE_HOURS=72`

## 第三步：部署

**先核对 Vercel 控制台** → [VERCEL_BUILD_SETTINGS.md](./VERCEL_BUILD_SETTINGS.md)（Framework 选 **Other**，Output 为 **`front/dist` 或与 vercel.json 一致**）。

```bash
cd /Users/Zhou/w/work/code/zmHairV
git push origin main   # 已连 GitHub 时 push 即触发部署
```

或本地 CLI：

```bash
vercel login
vercel --prod
```

或在 Vercel 导入 Git 仓库，**Root Directory** = `zmHairV`，保存后 **Redeploy**。

## 第四步：验收

1. 浏览器打开：`https://你的域名/health`  
   应看到 `"engine": "postgresql"` 且 `"persistent": true`。
2. 移动端：`/m/login` 用工号试登录。  
3. 管理端：`/admin/login`，`admin` / `admin123`（上线后建议在后台改密）。

首次访问 API 可能稍慢（冷启动 + 自动建表 + 种子数据），属正常。

## 第五步（可选）：导入本地 SQLite 数据

若 `back/zmhair.db` 里已有真实预约，且不想只用种子数据：

```bash
cd back
export DATABASE_URL='postgresql://...Neon连接串...'
./venv/bin/python scripts/migrate_sqlite_to_postgres.py
```

新环境无历史数据则**跳过**本步。

## 备份

Neon 控制台 → **Branches / Restore**：免费档含短时间 PITR；重要节点可手动 **Snapshot**。

## 本地开发

仍用 SQLite，不必改习惯：

```bash
cd back && ./start.sh
cd front && npm run serve
```

与线上共用 Neon 时，可在 `back/.env` 临时写 `DATABASE_URL=postgresql://...`（勿提交 Git）。

更多说明见 [persistence.md](./persistence.md)、[vercel.md](./vercel.md)。
