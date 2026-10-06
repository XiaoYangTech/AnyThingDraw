# 编译流程

本项目（亿方万能画笔 AnyThingDraw）是「智绘教 Inkeys」的修改版，编译方式与原项目一致。

对于一般的构建需求来说，你只需要构建 `AnyThingDraw.vcxproj` 即可，而该项目有一个附属项目 `PptCOM.csproj` 是 PPT 联动模块。  
`AnyThingDraw.vcxproj` 依赖于 `PptCOM.csproj` 生成的类库（dll/tlb）。  
**注意：如果只需要编译 `AnyThingDraw.vcxproj`，你需要在 `解决方案配置 -> 项目依赖项 -> AnyThingDraw` 中取消勾选 `PptCOM`，并使用 `-p:BuildProjectReferences=false` 参数构建（仓库中已内置预编译的 PptCOM.dll）。**

### 编译主项目 `AnyThingDraw.vcxproj`
本项目采用完全开源方式，所有源码和资源全部开源。

#### 准备环境
- Visual Studio 2022 (MSVC v143 编译器)
> 勾选 `使用 C++ 的桌面开发` `Windows 应用程序开发` 工作负荷
- Windows 11 SDK 10.26100

#### 代码环境
- Unicode
- C++20

#### 编译步骤
1. 拉取 `main` 仓库
2. 使用 Visual Studio 2022 打开 `AnyThingDraw.sln`
3. 选择 `AnyThingDraw` 项目
4. 切换为 `Release | x64` 构建配置（也可选择 `Win32` 或 `ARM64`，分别对应 32 位与 ARM64 架构）
5. 点击 `生成->Build AnyThingDraw` 即可

命令行方式（跳过 PptCOM 附属项目）：
```
msbuild "AnyThingDraw\AnyThingDraw.vcxproj" /p:Configuration=Release /p:Platform=x64 /p:BuildProjectReferences=false
```

---

### FAQ
某些特殊环境可能会导致无法编译。  
- **error LNK2001: 无法解析的外部符号 `std_search_1`**  
在 VS 2022 17.8.x（MSVC v143.35 ～ v143.41）中会导致无法编译。  

推荐使用 **17.14.x**，与项目开发者所安装的版本保持一致。（非必须）  

---

### 编译附属项目 `PptCOM.csproj`

#### 准备环境
- Visual Studio 2022
> 勾选 `.NET 桌面开发` 工作负荷
- .NET Framework 4.0 SDK 或更高版本

#### 编译步骤
1. 拉取 `main` 仓库
2. 使用 Visual Studio 2022 打开 `AnyThingDraw.sln`
3. 选择 `PptCOM` 项目
4. 切换为 `Release | AnyCPU`
5. 点击 `生成->Build PptCOM` 即可

---

### 自动构建与发布

推送 `v*` 形式的标签（如 `v1.0.0`）会触发 GitHub Actions 流水线：

1. 编译 Win32 / x64 / ARM64 三个架构
2. 使用 NSIS（`Installer/AnyThingDraw.nsi`）打包三架构安装包
3. 上传 GitHub Release，并同步到 CNB 仓库的 Release
4. 调用亿方智云 `ci_publish` 接口写入版本信息（供软件内自动更新使用）

所需仓库 Secrets：`CNB_TOKEN`（CNB 访问令牌）、`YF_RELEASE_TOKEN`（亿方智云后台「设置 → CI/CD 发布」生成）。
