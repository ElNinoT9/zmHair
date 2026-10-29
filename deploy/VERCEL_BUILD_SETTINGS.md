# Vercel 控制台 Build and Deployment 设置

打开：  
https://vercel.com/elninot9s-projects/zmhair/settings/build-and-deployment

改完后：**Deployments** → **Redeploy**（勾选 Use existing Build Cache 可取消，强制全量构建）。

## 必改项

| 设置项 | 正确值 | 错误示例 |
|--------|--------|----------|
| **Framework Preset** | **Other** | Vue.js（易导致只构建前端、API 不生效） |
| **Root Directory** | **留空** | `front` |
| **Node.js Version** | **20.x** | 18.x 可能构建失败 |
| **Build Command** | 关闭 Override，或 `npm run vercel-build` | 空且未读 vercel.json |
| **Output Directory** | 关闭 Override，或 **`front/dist`** | `.` 或 `dist` |
| **Install Command** | 关闭 Override，或 `cd front && npm install` | |

若 Dashboard 里 **Output Directory** 与 `vercel.json` 不一致，以 **vercel.json 的 `front/dist`** 为准（建议 Dashboard Override **关掉**，避免冲突）。

## 环境变量

Settings → Environment Variables：

- `DATABASE_URL` = Neon 连接串（Production + Preview）
- `SECRET_KEY` = 随机长串

未配 `DATABASE_URL` 时，接口启动会报错（故意防止 SQLite 无持久化）。

## 代码更新后

Git 已连接时 push `main` 会自动部署；或 Deployments → **Redeploy**。

## 验收

- `https://你的域名.vercel.app/health`
- `/m/login`、`/admin/login`

失败时打开该次 Deployment 的 **Build Logs**，把末尾报错复制排查。
