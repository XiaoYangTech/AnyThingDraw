<p align="center">
  <img src="GithubRes/logo.png" width="128" alt="亿方万能画笔 Logo">
</p>

<h1 align="center">亿方万能画笔</h1>

<p align="center">
  <a href="https://github.com/XiaoYangTech/AnyThingDraw">GitHub</a> ·
  <a href="https://cnb.cool/InspireWorks/AnyThingDraw">CNB</a> ·
  <a href="https://draw.yfyw.top/">官网</a>
</p>

<p align="center">一款面向课堂教学的屏幕批注与演示辅助工具，基于开源项目「智绘教 Inkeys」二次开发，针对教学实际环境做了大量删减与修改。软件基于 C++20 编写，专为 Windows 平台打造。</p>

---

**Copyright © 2026 InspireWorks（亿方运维）** · 基于「智绘教 Inkeys」（Copyright © 2023-2025 AlanCRL（陈润林）工作室，GPL-3.0）二次开发

## 本项目说明

本软件是 [智绘教 Inkeys](https://github.com/Alan-CRL/Inkeys)（作者 Alan-CRL）的修改版，与原项目相比的主要变化：

- **功能精简**：删除了教学场景中用不到的模块（原作者已不再维护的 Inkeys2 系列皮肤系统、部分第三方社区点名器等）和死代码，软件更轻量、更贴合课堂的实际使用环境。
- **对齐上游**：画笔弹窗拦截、PPT 联动等核心功能与上游版本保持同步。
- **人性化逻辑**：新增并调整了多处细节交互——触摸设备自动识别、橡皮清空逻辑、PPT 工具栏行为、不分文案调整等。
- **界面与设置优化**：全面梳理界面文本，合并重复设置项，清理无效入口与冗余选项。

## 下载与要求

- 官网下载页：<https://draw.yfyw.top>
- GitHub Releases：<https://github.com/XiaoYangTech/AnyThingDraw/releases>

提供 32 位 / 64 位 / ARM64 三种处理器的安装包（NSIS），支持软件内自动更新。  
最低支持 Windows 7 (RTM, sp0)，支持 32 位 / 64 位 / Arm64 系统。

## 反馈

问题报告与功能建议请前往 [GitHub Issues](https://github.com/XiaoYangTech/AnyThingDraw/issues)。

## 许可证

本项目基于 [GNU General Public License v3.0](LICENSE) 获得许可。

**修改声明**：本软件是「智绘教 Inkeys」（Copyright © 2023-2025 AlanCRL（陈润林）工作室，GPL-3.0）的修改版本，
由 InspireWorks（亿方运维）自 2026 年起修改与发布。
原始版权声明、`NOTICE` 与 `ThirdpartyLicenses/` 均完整保留；
本修改版的对应源代码发布于 <https://github.com/XiaoYangTech/AnyThingDraw>。

## 编译说明

编译步骤见 [编译流程](CompilationProcess.md)（Visual Studio 2022 + MSVC v143）。

## 项目引用

### 第三方开源组件

我们在此对这些开源项目及其贡献者表示感谢。以下为部分主要第三方组件及其许可信息（仅为摘要，具体约束以各组件随附许可证文本为准）：

| 组件名称 | 许可证 | 版权信息 / 说明 |
| :--- | :--- | :--- |
| **[abseil/abseil-cpp](https://github.com/abseil/abseil-cpp)** | Apache License 2.0 |  |
| **[aksalj/hashlibpp](https://github.com/aksalj/hashlibpp)** | 参见库内 LICENSE / 说明文件 | Copyright (c) 2007–2011 Benjamin Gr¸delbach |
| **[Alan-CRL/DesktopDrawpadBlocker](https://github.com/Alan-CRL/DesktopDrawpadBlocker)** | GNU General Public License v3.0 |  |
| **[cameron314/concurrentqueue](https://github.com/cameron314/concurrentqueue)** | 参见库内 LICENSE / 说明文件 | Copyright (c) 2013–2016, Cameron Desrochers. All rights reserved. |
| **[efficient/libcuckoo](https://github.com/efficient/libcuckoo)** | 参见库内 LICENSE / 说明文件 | Copyright (C) 2013, Carnegie Mellon University and Intel Corporation |
| **[gabime/spdlog](https://github.com/gabime/spdlog)** | MIT License | Copyright (c) 2016 Gabi Melman. |
| **[google/ink-stroke-modeler](https://github.com/google/ink-stroke-modeler)** | Apache License 2.0 |  |
| **[martinus/unordered_dense](https://github.com/martinus/unordered_dense)** | MIT License | Copyright (c) 2022 Martin Leitner-Ankerl |
| **[mohabouje/WinToast](https://github.com/mohabouje/WinToast)** | MIT License | Copyright (C) 2016–2023 WinToast v1.3.0 - Mohammed Boujemaoui <mohabouje@gmail.com> |
| **[nothings/stb](https://github.com/nothings/stb)** | MIT License | Copyright (c) 2017 Sean Barrett |
| **[ocornut/imgui](https://github.com/ocornut/imgui)** | MIT License | Copyright (c) 2014–2025 Omar Cornut |
| **[openssl/openssl](https://github.com/openssl/openssl)** | Apache License 2.0 | Copyright (c) 1998–2025 The OpenSSL Project Authors. Copyright (c) 1995–1998 Eric A. Young, Tim J. Hudson. All rights reserved. |
| **[open-source-parsers/jsoncpp](https://github.com/open-source-parsers/jsoncpp)** | MIT License | Copyright (c) 2007–2010 Baptiste Lepilleur and The JsonCpp Authors |
| **[sammycage/lunasvg](https://github.com/sammycage/lunasvg)** | MIT License | Copyright (c) 2020–2025 Samuel Ugochukwu <sammycageagle@gmail.com> |
| **[sammycage/plutovg](https://github.com/sammycage/plutovg)** | MIT License | Copyright (c) 2020–2025 Samuel Ugochukwu <sammycageagle@gmail.com> |
| **[yhirose/cpp-httplib](https://github.com/yhirose/cpp-httplib)** | MIT License | Copyright (c) 2017 yhirose |
| **[Zip Utils](https://www.codeproject.com/Articles/7530/Zip-Utils-Clean-Elegant-Simple-Cplusplus-Win)** | 参见项目页面及随附许可证 |  |
| **[zouhuidong/HiEasyX](https://github.com/zouhuidong/HiEasyX)** | MIT License | Copyright (c) 2022 zouhuidong |

关于本软件使用的所有第三方库的**完整列表**及其对应的许可证文本，请查阅：

- **主要组件声明（NOTICE）**：  
  <https://github.com/XiaoYangTech/AnyThingDraw/blob/main/NOTICE>
- **第三方许可证文件汇总**：  
  <https://github.com/XiaoYangTech/AnyThingDraw/tree/main/ThirdpartyLicenses>

> 当本声明与上述第三方组件的许可证存在冲突或不一致时，  
> 就相关第三方组件的使用、复制、修改和分发事宜，以相应第三方许可证的具体条款为准。

### 第三方组件

除上述开源组件外，本软件在开发和运行过程中还可能使用部分以其他许可方式授权的第三方库或工具。我们同样对这些项目的作者和维护者表示感谢。

以下为目前使用的部分非（或不完全）开源组件及其授权信息摘要（如有）：

| 组件名称 | 许可授权 / 使用说明 |
| :--- | :--- |
| **[EasyX](https://easyx.cn/)** | 根据 EasyX 官方网站公布的授权条款使用。具体权利义务以 EasyX 官方的最新授权条款为准。 |

> 我们对第三方组件的使用不构成对其项目的任何所有权声明。  
> 您在独立使用上述第三方软件、库或服务时，仍应仔细阅读其各自的使用条款和许可证，并自行遵守。

## 其他内容

本软件与原项目「智绘教 Inkeys」的发展方向不同，如需了解原项目，请访问：

- 原项目仓库：<https://github.com/Alan-CRL/Inkeys>
- 原项目官网：<https://www.inkeys.top>
