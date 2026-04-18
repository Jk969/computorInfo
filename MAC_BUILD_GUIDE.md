# Mac 客户端编译与使用说明

由于在 Windows 环境下无法直接编译 macOS 应用程序，本工程引入了 **GitHub Actions** 来实现在云端（免费）自动编译 Mac 客户端的功能。编译出的程序将使用 `universal2` 架构，**完美兼容 Intel 处理器的旧款 Mac 以及 M1/M2/M3 (Apple Silicon) 的新款 Mac**。

## 目录结构说明
- `client_mac/`: 存放专门针对 macOS 编写的采集代码。避免与 Windows 代码混用引发报错。
- `.github/workflows/build_mac.yml`: 控制 GitHub 服务器自动帮您打包的配置文件。

---

## 如何在云端编译 Mac 客户端？

### 前提条件
您需要拥有一个 [GitHub](https://github.com/) 账号。

### 步骤
1. **上传代码到 GitHub**：
   将您电脑上的当前工程（至少包含 `client_mac` 和 `.github` 目录）推送到 GitHub 的一个代码仓库中。
   ```bash
   git init
   git add .
   git commit -m "init"
   git branch -M main
   git remote add origin https://github.com/您的用户名/您的仓库名.git
   git push -u origin main
   ```

2. **触发编译**：
   - 当您把代码 `push` 到 GitHub 仓库时，GitHub Actions 会**自动触发**编译任务。
   - 或者，您也可以打开该仓库的网页，点击顶部的 **Actions** 标签页，在左侧选择 `Build Mac Client`，然后点击右侧的 **Run workflow** 按钮手动触发。

3. **下载成品**：
   - 编译过程大约需要 1~2 分钟。
   - 编译完成后，点击进入这次执行成功的运行记录（通常有个绿色的对勾 ✅）。
   - 滚动到页面底部的 **Artifacts** 区域。
   - 点击 **`MacInfoCollector-Universal-App`** 即可下载到一个 `zip` 压缩包。

---

## 如何在 Mac 上运行？

1. **解压**：将下载下来的 `zip` 文件发送给使用 Mac 的员工并解压。
2. **运行**：解压后会得到一个名为 `MacInfoCollector.app` 的程序图标，直接双击运行即可。

> **⚠️ Mac 运行提示 (重要)**：
> 由于这个应用程序是我们自己打包的，没有经过苹果官方 99 美元/年的开发者签名，Mac 默认的安全机制可能会阻止它运行并提示“无法验证开发者”。
> **解决方法：**
> 让员工在 `MacInfoCollector.app` 上点击鼠标**右键**（或按住 Control 键点按），在弹出的菜单中选择 **“打开”**。系统会弹出一个确认框，再次点击“打开”即可正常运行。之后就不需要再这样操作了。