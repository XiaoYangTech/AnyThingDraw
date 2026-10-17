# AnyThingDraw 项目约定

## Git 工作流

- 提交信息使用中文，前缀 `fix:` / `feat:`。
- **关键改动：本地提交后立即推送到远程，无需再单独请示。**
  - `git push origin main` 一次推送会同时发到 cnb.cool 与 GitHub（origin 配了两个 push 地址）。
- 与任务无关的他人改动（如莫名的文件删除）不要纳入提交。

## 版本与开发代号

- 每个版本的开发代号按时间顺序与中国地理挂钩：从泰安市泰山区开始，第一个版本名为泰山，之后向外扩展，从山河四省到全国。
- 每个代号都要配以解释，说明为什么用这个词（写入 RELEASE_NOTES.md 引言）。
- 发布提交格式 `feat: 发布 vX.X.X（开发代号：X）`，tag 格式 `vX.X.X`；文案写入根目录 RELEASE_NOTES.md 随版本号一起提交，推送 tag 自动触发三平台构建。
- **RELEASE_NOTES.md 是覆盖式维护**：`.github/workflows/release.yml` 会把整个文件当作当版 GitHub Release 正文，发版时必须用新版本说明**整体覆盖**旧内容，禁止往上追加历史段落——追加会让上一版内容重复出现在新 Release 正文里。历史发布说明以各平台 Releases 页面为准，无需在文件里保留。请不要把无关紧要的更新内容（比如文案的修改，部分和修复bug、功能新增无关的内容，亦或是服务器后端的更新内容）写进此文件。

## 当前状态（2026-10-17 交接）

- 上一轮 ZCode 会话因思考通道退化（星号/括号嵌套乱码）作废，完整交接见 [`docs/zcode-handoff.md`](docs/zcode-handoff.md)：项目身份、环境、18 项需求完成状态、批 4a 崩溃现场、下一步顺序。
- HEAD = `4962eb1c`，工作区干净，**ahead 3 未推送**：`9548dbaa`（删超级置顶/快捷方式保障 + DDB 回滚上游）、`e5ef6209`（用户数据目录迁 `%LOCALAPPDATA%`）、`4962eb1c`（橡皮过渡 + WPS 焦点）。
- 批 4a（设置页侧边栏：`插件`→`演示`+`悬浮窗`、`组件`→`界面`）**未完成**；改坏的 `AnyThingDraw/ATDrawSetting.cpp` 已回滚到 HEAD，损坏版本备份在 `D:\开发\AnythingDraw\zcode-broken-ATDrawSetting.cpp.bak`。
- 数据目录已在 `%LOCALAPPDATA%\AnyThingDraw`；安装目录只应放程序本体、`PptCOM.dll`、`exe/DesktopDrawpadBlocker.exe`。
- 改 `ATDrawSetting.cpp` 时不要再用「整块脚本删除 + 括号配平」；按 tab 小步改、每步编译。
- 2026-10-01~10-06 的历史改造账目（品牌/i18n/死代码/云 API/CI 发布流水线/构建坑）见 `docs/zcode-memory/inkeys-fork-dev-setup.md`。
