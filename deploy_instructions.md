# 电脑信息自动采集系统部署指南

## 1. 后端服务部署 (Node.js)

后端服务需要部署到公网服务器 `47.109.135.123`，并对外暴露 `36867` 端口。

### 部署步骤
1. **连接服务器**：
   打开终端，输入您的自定义命令连接公网服务器：
   ```bash
   ssh al
   ```
2. **上传代码**：
   将本机的 `server` 文件夹及其内容（`app.js`, `package.json`, `public/` 等）上传到服务器。
   （您可以通过 `scp -r server root@47.109.135.123:/root/pc-info-server` 进行上传）
3. **安装环境**：
   在服务器上确保已安装 Node.js。然后进入 `server` 目录执行安装依赖：
   ```bash
   cd /root/pc-info-server
   npm install
   ```
4. **启动服务**：
   为了让服务在后台常驻运行，推荐使用 `pm2`：
   ```bash
   npm install -g pm2
   pm2 start app.js --name pc-info-collector
   ```
   *或者直接前台运行测试：*
   ```bash
   node app.js
   ```
5. **防火墙配置**：
   确保服务器安全组和系统防火墙放行了 **36867** 端口。

---

## 2. 客户端发布 (Windows)

1. 在开发机器上，进入 `client` 目录。
2. 双击运行 `build.bat`。
3. 编译完成后，进入 `client/dist/` 文件夹。
4. 将里面生成的 `PCInfoCollector.exe` 发送给需要采集信息的员工。
5. 员工双击运行该程序，填写“采购年份”和“使用人”后点击提交即可。

### 注意事项：
> 客户端代码中的 `SERVER_URL` 目前指向的是本地测试地址（`http://localhost:36867/api/report`），或者如果您已经改回了公网地址，请在发版前确认 `main.py` 中的 `SERVER_URL = "http://47.109.135.123:36867/api/report"`。如果需要重新编译，修改代码后再次运行 `build.bat` 即可。