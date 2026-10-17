# AnyThingDraw — zcode 会话交接文档（DSH 接手用）

> 生成时间：2026-10-17 19:20（Asia/Shanghai）
> 来源：ZCode（清华 agent）会话 `sess_a79107ad-55e9-4f31-9bab-0c2d488c5ee7`，cwd `D:\开发\AnythingDraw`，18 轮人工输入 / 16 个 Explore 子代理。
> 该会话因**思考通道退化**（见 §7）作废，不是任务失败。本文件 + 仓库现状用于在 DSH 中继续。

## 1. 项目身份与环境

| 项 | 值 |
|---|---|
| 上游 | Alan-CRL/Inkeys「智绘教」，GPL-3.0，C++20 / MSVC v143 / EasyX / ImGui |
| 二创品牌 | 亿方万能画笔（中文）/ AnyThingDraw（英文） |
| 主体 | InspireWorks（亿方运维），作者「小杨聊科技」，邮箱 admin@yfyw.top，B站 UID 413043448 |
| 官网 | https://draw.yfyw.top |
| 仓库根 | `D:\开发\AnythingDraw\AnyThingDraw`（源码在 `AnyThingDraw\` 子目录，vcxproj 同层） |
| 运行目录 | `D:\Software\AnyThingDraw\` |
| 云 API 文档 | `D:\开发\InspireWorksCloud\docs\api-reference.md` |
| NSIS | `D:\Software\NSIS\makensis.exe`，脚本 `Installer/AnyThingDraw.nsi`（**必须 UTF-8 BOM**） |

**远程**：`origin` = github.com/XiaoYangTech/AnyThingDraw（同一 remote 配了两个 push url，另一个是 cnb.cool/InspireWorks/AnyThingDraw）；另有独立 remote `cnb`。
**git 身份**：XiaoYangTech / yangxiaoxu2041@qq.com（repo local 有 dev@yfyw.top）。
**网络坑**：repo local `http.proxy=127.0.0.1:7897`（Clash）。直连 GitHub 不稳，push 常需循环重试 3–5 次、间隔 8s；Clash 关掉后代理端口会死，需 `git -c http.proxy= push origin main`。

**构建命令**（在 `AnyThingDraw\AnyThingDraw\` 下）：
```bat
taskkill /F /IM MSBuild.exe /IM cl.exe
"D:\Software\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\MSBuild.exe" AnyThingDraw.vcxproj -p:Configuration=Release -p:Platform=x64 -p:BuildProjectReferences=false -m -v:m -nologo
```
产物：`x64\Release\AnyThingDraw.exe`；部署=复制到 `D:\Software\AnyThingDraw\` 后启动。

## 2. 当前 git 状态（重要）

- HEAD = `4962eb1c`，工作区**干净**，**ahead 3 未推送**。
- 未推送：`9548dbaa`（删超级置顶+快捷方式保障、DDB 回滚上游）、`e5ef6209`（数据目录迁 %LOCALAPPDATA%）、`4962eb1c`（橡皮过渡+WPS 焦点）。
- 批 4a（设置页重构）改坏过 `AnyThingDraw/ATDrawSetting.cpp`，已**回滚到 HEAD**；损坏版本备份在 `D:\开发\AnythingDraw\zcode-broken-ATDrawSetting.cpp.bak`。
- 当前已编译验证通过（2026-10-17 19:19）。

## 3. 用户 18 项需求的完成状态

原话见 §6。状态：✅完成 / 🔶部分 / ⬜未开始 / ❓待回答。

| # | 需求 | 状态 | 落点 |
|---|---|---|---|
| 1 | 修复打包安装到 C 盘无法运行（被重定向） | ✅ | `e5ef6209`：数据目录迁到 `%LOCALAPPDATA%\AnyThingDraw`，旧配置自动迁移 |
| 2 | 避免与 PPT 软件权限不一致导致 COM 异常 | ✅ | 同提交：PptCOM.dll 复用安装包文件，缺 DLL 才从资源释放 |
| 3 | DDB 已打包进程序，其「管理员权限运行」设置项还有用吗 | ❓ | 建议：DDB 由主程序以 `hostPath` 启动，若其自身再提权会破坏宿主-窗口联动，**应保持关闭甚至从 DDB UI 移除**（待你在新会话确认） |
| 4 | 橡皮双击后短暂变鼠标再回批注 | ✅ | `4962eb1c`：新增 `GetDisplayModeForUi`，清空过渡期 UI 保持橡皮外观 |
| 5 | 删「快捷方式保障」（NSIS 已管理） | ✅ | `9548dbaa` |
| 6 | 删「超级置顶」（鸡肋且可能致 PPT 联动失效） | ✅ | `9548dbaa`：含三段式提权、UiAccess、pin 资源、配置项 |
| 7 | PPT 演示助手 / 悬浮窗拦截拆成「演示」「悬浮窗」两个设置项 | 🔶 | 批 4a 做到一半被回滚，需重做 |
| 8 | 重构现有设置项分类、合并整理 | ⬜ | 依赖 #7 |
| 9 | 「组件」改名「界面」 | ⬜ | 回滚后仍是「组件」，一行改动 |
| 10 | 恢复原版「只允许一个按钮」提示；只允许同时开一个组件按钮 | ⬜ | 源码中已无相关文案（grep 无命中） |
| 11 | PPT 演示助手「大纲视图」设置项只显示一半 | ⬜ | 相关 UI 在 `ATDrawSetting.cpp` 约 4745–4770 行（「点击中间页码打开大纲视图」） |
| 12 | PPT 三个「侧边栏缩放」统一成一个滑动条 | ⬜ | 现为三个独立 `SliderFloat`：底部两侧 5040 / 中部两侧 5175 / 底部主栏 5316 行 |
| 13 | 「中部两侧工具栏」改名「左右两侧工具栏」 | ⬜ | 字符串在 `ATDrawSetting.cpp:4660`（「显示中部两侧控件」）、5175 等 |
| 14 | 「中部两侧 PPT 控件」上方空白，改成下方那种控件模式 | ⬜ | 同 #13 区域 |
| 15 | 窗口切换退出放映时记录日志；排查 WPS 刚点放映就秒退 | ✅ | `4962eb1c`：`IsPptShowForeground` → `GetPptFocusState` 三态 + 防抖确认 + 启动冷却 + 日志 |
| 16 | 恢复上游 DDB 原版代码（改版会误拦截，原版已修） | ✅ | `9548dbaa`：DDB 回滚 `a8707f5`，重编译替换内嵌 exe（sha256 `7c3472ba…`） |
| 17 | 打包版目录下一堆空白文件夹，可删 | ⬜ | 仍有 `ATDrawSetting.cpp:234 installerDir = globalPath+"installer"`、`ATDrawMain.cpp:829 PptCOM.dll` 等安装目录写入；`create_directories` 调用点共 8 处 |
| 18 | 两个设置 json 统一为一个 | ⬜ | `ATDrawConfiguration.cpp:89-90` 仍分别 migrate `opt\deploy.json` + `opt\pptcom_configuration.json` |

## 4. 已完成的 3 个提交做了什么

### `9548dbaa` 删超级置顶 / 删快捷方式保障 / DDB 回滚
- `ATDrawMain.cpp`：删 `superTopComplete` 与命令行分支、SuperTop 启动阶段块、FailSignal 配置修正；删 `SetShortcut` 调用。
- `ATDrawSetting.cpp`：删 SuperTop 设置页（约 62 行残留）、插件卡、`tabSuperTop` 枚举；删快捷方式保障设置页（228 行）、插件卡（63 行）、基础设置「创建快捷方式」卡（68 行）。
- `ATDrawConfiguration.*`：删 `ReadSettingMini`、`plugInSetting.superTop` 结构。
- `ATDrawPlug-in.*`：删 `ShortcutAssistantClass` 及其实现（124 行）。
- 资源：删 `ICON21`、`src/pin.png`、vcxproj/filters 对应条目。
- DDB：`git reset --hard a8707f5`，MSBuild 重编，替换 `AnyThingDraw\exe\DesktopDrawpadBlocker.exe`。

### `e5ef6209` 数据目录迁移
- 新增 `userDataPath`（`%LOCALAPPDATA%\AnyThingDraw\`），`globalPath` 仅保留 exe 目录语义。
- 迁移对象：配置、日志、installer、插件、崩溃转储、画笔记忆；含旧配置自动迁移（`migrate()`）。
- `pluginPath = userDataPath`；`typeRoot` 检测逻辑删除。

### `4962eb1c` 橡皮过渡 + WPS 焦点
- `ATDrawFloating.cpp` / `ATDrawState.cpp`：新增 `GetDisplayModeForUi()`，清空画布过渡期间 6 处橡皮/选择展示判断改用它，消除「橡皮→鼠标→批注」闪现。
- `ATDrawPlug-in.cpp`：`IsPptShowForeground()` 替换为 `GetPptFocusState()` 三态（前景/后台/未知）+ 防抖确认 + 放映启动冷却 + 焦点切换日志。

## 5. 批 4a 崩溃现场（重做前必读）

**目标**：侧边栏 `插件` 拆成 `演示` + `悬浮窗` 两项；删旧「插件」页三子页（PPT 助手 / DDB / 快捷方式）；`组件` → `界面`。

**做法**：zcode 用 Python 脚本按**行号切片**改 `ATDrawSetting.cpp`（`redo_tabs.py` 最后版在 `D:\开发\AnythingDraw\redo_tabs.py`，另见 `patch_tabs.py`、`fix_sidebar.py`）。

**翻车链**：
1. 首次按「括号配平」定位块边界，误把 7263 行当按钮块插入 → 文件膨胀到 8433 行 → 回滚。
2. 改行号切片后，删「DDB 返回按钮」时把外层 `{` 删掉但它的 `}` 还在 → `switch` 提前结束 → 编译 `C2046 非法的 case`（6723/7140 行）。
3. 修一版又出现 `io 未声明`（函数体被提前闭合）。
4. 此时思考通道开始退化（§7），会话终止。

**新会话建议**：不要再用整块脚本删除 + 配平。改成**一个 tab 一个 tab 小步改、每步编译**；或直接手工编辑。`ATDrawSetting.cpp` 主函数约 8379 行，`settingTabEnum` 在 921–936 行附近。

## 6. 用户原始需求（HUMAN 763 原文，逐项）

> 修复打包后安装在C盘无法运行，提示被重定向，但是要避免因为和PPT软件权限不一导致的COM组件异常。现在的DDB打包进程序了，那里面那个管理员权限运行的设置项还有用吗？修复橡皮双击后会短暂到鼠标再到批注，修复插件多余：快捷方式保障工作是NSIS管理的，不需要插件。超级置顶功能鸡肋，且可能导致PPT联动失效，删掉。剩下的PPT演示助手和悬浮窗拦截，可以放到单独设置项（演示和悬浮窗）。重构目前已有的设置项分类，看看能不能合并整理。组件设置项要不改一个名字叫界面。把原版的只允许一个按钮的提示加回来，只允许同时打开一个组件按钮。PPT演示助手里面的大纲视图设置项只显示一半，另一半看不见。PPT插件三个侧边栏缩放统一成一个滑动条。中部两侧工具栏改名叫左右两侧工具栏。中部两侧PPT控件上方有空白。要改成类似下方那种控件的模式。因为窗口切换退出放映时候记录日志，并排查一下为啥现在用WPS 有些时候刚点放映就被秒退出，重启电脑后正常（我的另一台电脑）。恢复上游DDB原始代码，目前改版会导致误拦截。原版已经修复了。程序打包版目录下会产生有一堆空白文件夹，可以删掉。有两个不同的设置项json，可以统一为一个。

## 7. 为什么必须放弃那个 zcode 会话

思考通道退化，不是普通「上下文太长」：

| 证据 | 数值 |
|---|---|
| 最后 3 次响应思考文本星号数 | 954 / 658 / 816 个 |
| 星号占比 | 34.1% / 35.7% / 35.7% |
| 形态 | 嵌套括号 + 星号交替，如 `（**外层 `{`**（**5586-5592**）**））`，语义自我覆盖 |
| 自述 | msg 909：`用户指出："你的思考过程怎么多了这么多星号"` |

结论：上下文已被这种输出污染，在同一位置会持续打转，**修上下文不如换会话**。恢复方法是本文件 + 干净 HEAD。

## 8. 建议的下一步顺序

1. **先推送**（3 个提交在本地）：`git -c http.proxy= push origin main`，失败就隔 8s 重试 3–5 次。
2. **重做批 4a**（#7 + #9），小步改、每步编译。
3. #10–#14 设置页 UI 小项。
4. #17 空白文件夹、#18 两个 json 合并。
5. 回答 #3（DDB 权限设置项）。

## 9. 原始证据与提取物位置

| 内容 | 路径 |
|---|---|
| 完整对话 rollout（72 次模型请求，27MB） | `C:\Users\Admin\.zcode\cli\rollout\model-io-sess_a79107ad-*.jsonl` |
| zcode 主数据库（18 会话 / 3568 消息） | `C:\Users\Admin\.zcode\cli\db\db.sqlite` |
| 16 个 Explore 子代理任务与产出 | `C:\Users\Admin\.zcode\cli\agents\sess_a79107ad-*\` |
| zcode 项目记忆（已复制入库） | `docs/zcode-memory/` |
| 清洗后全文 / 最后一条需求之后的时间线 | `D:\开发\AnythingDraw\zcode-import\transcript.md`、`tail.md` |
| 星号退化分析脚本 | `D:\开发\AnythingDraw\zcode-import\analyze_stars.py` |
| 改坏的文件备份 | `D:\开发\AnythingDraw\zcode-broken-ATDrawSetting.cpp.bak` |

## 10. 项目历史记忆

zcode 在 2026-10-01 ~ 10-06 期间积累的完整改造账目（品牌替换、i18n 删除、皮肤/点名器删除、死代码清理、亿方智云 API、三架构自动更新、CI 发布流水线、CNB 凭证与大包坑、构建坑清单）见：
`docs/zcode-memory/inkeys-fork-dev-setup.md`（原文照搬，未改动）。
继续开发前建议先读它，尤其是「操作坑（血泪）」一节。
