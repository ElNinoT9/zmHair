# 企业内部理发预约管理系统

前后端分离：Vue 2 + Element UI / Vant + FastAPI + SQLite

```
zmHair/
├── back/     # 后端 API
├── front/    # 前端页面
└── README.md
```

## 启动

**后端**
```bash
cd back
./start.sh
```

**前端**
```bash
cd front
./start.sh
```

- 后端：http://127.0.0.1:8001/docs
- 前端开发：http://127.0.0.1:8080
- 账号：`admin` / `admin123`（PC 管理后台）
- H5 移动端：输入工号即可，无需密码，自动记住登录

## 测试账号

| 角色 | 工号 | 密码 | 说明 |
|------|------|------|------|
| 管理员 | admin | admin123 | PC 管理后台 `/admin/login` |
| 理发师 | 094164 / 094165 / 094026 | 无需密码 | 贾艳争、张岳骁、骆春晖（H5 工作台） |
| 普通员工 | 094189 等 | 无需密码 | H5 预约理发 / 我的预约 |

## 配置

后端默认端口 **8001**，可在 `back/.env` 中修改：

```
PORT=8001
SECRET_KEY=your-secret-key
```

`start.sh` 启动时会自动释放被占用的端口，并在 Python 版本不兼容时重建虚拟环境。

## 当前功能

| 模块 | 说明 |
|------|------|
| PC 管理后台 | 用户权限管理、预约台账、Excel 导出、系统配置 |
| H5 员工端 | 理发师列表、按日期预约、个人预约记录 |
| H5 理发师端 | 排班设置（7~14 天）、预约订单、站内消息通知 |

## 业务规则

1. 登录凭证为员工工号，系统自动匹配姓名
2. 预约对象为【理发师 + 预约日期】，不做分钟级时段锁定
3. 具体理发时间由理发师线下沟通，系统仅作登记台账
4. 预约成功后推送站内消息给理发师

## 生产部署（单域名）

域名：**http://hair.cnmc-clm.com.cn**

| 入口 | 地址 |
|------|------|
| 移动端 H5 | http://hair.cnmc-clm.com.cn/m/login |
| PC 管理后台 | http://hair.cnmc-clm.com.cn/admin/login |

同一域名、不同路径；`/api` 由 Web 服务器反向代理到本机 8001 端口。

**详细步骤见 [deploy/部署说明.md](deploy/部署说明.md)**（内网 IIS/Nginx）

**Vercel + Neon 上线清单见 [deploy/neon-quickstart.md](deploy/neon-quickstart.md)**

**持久化说明见 [deploy/persistence.md](deploy/persistence.md)**

快速命令：

```bash
# 1. 后端（生产）
cd back && cp .env.example .env   # 修改 SECRET_KEY
./start_prod.sh                   # Windows: start_prod.bat

# 2. 前端打包
./deploy/build.sh                 # Windows: deploy\build.bat

# 3. 将 front/dist 部署到 IIS 或 Nginx（见 deploy 目录配置）
```
