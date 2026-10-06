; ============================================================
; 亿方万能画笔 AnyThingDraw 安装程序（NSIS 3.x / Unicode）
;
; 三架构：makensis /DARCH=ia32|x64|arm64 编译出对应安装包
;   ia32  → 32 位程序（32 / 64 位系统均可运行）
;   x64   → 64 位程序（需要 64 位 Windows）
;   arm64 → ARM64 程序（需要 ARM64 Windows）
;
; CI 用法：
;   makensis /DARCH=x64 /DAPPVERSION=1.0.0 /DSRCDIR=dist\x64 ^
;            /DARCH64URL=<64位安装包下载地址> /DARCHARM64URL=<ARM64下载地址> ^
;            /DOUTDIR=out AnyThingDraw.nsi
;
; 特性：请求 UAC 提权、默认安装到 Program Files\AnyThingDraw、
;       32 位安装包在 64 位处理器上引导安装 64 位 / ARM64 版本、
;       不显示 EULA、支持覆盖安装（结束运行中的旧版本后直接覆盖）
; ============================================================

Unicode true

!include "MUI2.nsh"

!ifndef ARCH
  !define ARCH "x64"
!endif
!ifndef APPVERSION
  !define APPVERSION "1.0.0"
!endif
!ifndef SRCDIR
  !define SRCDIR "."
!endif
!ifndef OUTDIR
  !define OUTDIR "."
!endif
!ifndef ICONPATH
  !define ICONPATH "AnyThingDraw\src\icon.ico"
!endif
!ifndef ARCH64URL
  !define ARCH64URL ""
!endif
!ifndef ARCHARM64URL
  !define ARCHARM64URL ""
!endif

!define APPNAME "AnyThingDraw"
!define APPDISPLAY "亿方万能画笔 AnyThingDraw"
!define PUBLISHER "InspireWorks（亿方运维）"
!define UNINSTKEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\AnyThingDraw"

Name "${APPDISPLAY}"
OutFile "${OUTDIR}\atdraw-${APPVERSION}-Setup-${ARCH}.exe"

; 默认安装到 Program Files\AnyThingDraw（32 位包在 64 位系统会被引导装 64 位版）
!if "${ARCH}" == "ia32"
  InstallDir "$PROGRAMFILES\AnyThingDraw"
!else
  InstallDir "$PROGRAMFILES64\AnyThingDraw"
!endif
InstallDirRegKey HKLM "Software\AnyThingDraw" "InstallDir"

; 请求管理员权限（UAC）
RequestExecutionLevel admin
SetCompressor /SOLID lzma
Icon "${ICONPATH}"
UninstallIcon "${ICONPATH}"

; 页面：安装目录 → 安装进度（无 EULA 页）
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "SimpChinese"

Function .onInit
  ; ---- 处理器位数判定（不依赖任何插件，读 WOW64 环境变量）----
  ; 64 位 Windows 上运行的 32 位进程：PROCESSOR_ARCHITEW6432 = AMD64 / ARM64
  ; 纯 32 位 Windows：该变量不存在
  ReadEnvStr $0 "PROCESSOR_ARCHITEW6432"

!if "${ARCH}" == "ia32"
  StrCmp $0 "" ia32_done
  StrCmp $0 "ARM64" ia32_guide_arm64
  StrCmp $0 "AMD64" ia32_guide_x64
  Goto ia32_done

ia32_guide_x64:
  !if "${ARCH64URL}" != ""
    MessageBox MB_YESNO|MB_ICONQUESTION "检测到您的计算机使用 64 位处理器。推荐安装 64 位版本，以获得更好的性能与兼容性。$\n$\n是否现在下载 64 位安装包？" IDNO ia32_done
    ExecShell "open" "${ARCH64URL}"
    Abort
  !endif
  Goto ia32_done

ia32_guide_arm64:
  !if "${ARCHARM64URL}" != ""
    MessageBox MB_YESNO|MB_ICONQUESTION "检测到您的计算机使用 ARM64 处理器。推荐安装 ARM64 版本，以获得更好的性能与兼容性。$\n$\n是否现在下载 ARM64 安装包？" IDNO ia32_done
    ExecShell "open" "${ARCHARM64URL}"
    Abort
  !endif
  Goto ia32_done

ia32_done:
!endif

!if "${ARCH}" == "x64"
  ReadEnvStr $0 "PROCESSOR_ARCHITECTURE"
  StrCmp $0 "x86" x64_block32
  Goto x64_done
x64_block32:
  MessageBox MB_OK|MB_ICONSTOP "此安装包为 64 位版本，无法安装在 32 位 Windows 上。$\n请下载 32 位安装包。"
  Abort
x64_done:
!endif

!if "${ARCH}" == "arm64"
  ReadEnvStr $0 "PROCESSOR_ARCHITECTURE"
  StrCmp $0 "ARM64" arm64_done
  MessageBox MB_OK|MB_ICONSTOP "此安装包为 ARM64 版本，无法安装在此设备上。$\n请下载与设备匹配的安装包。"
  Abort
arm64_done:
!endif
FunctionEnd

Section "AnyThingDraw" SecMain
  SetShellVarContext all

  ; 覆盖安装：结束正在运行的旧版本
  nsExec::Exec 'taskkill /IM AnyThingDraw.exe /F'
  Pop $0
  Sleep 600

  SetOutPath "$INSTDIR"

  ; 覆盖旧文件（切换架构时防止旧文件残留）
  Delete "$INSTDIR\AnyThingDraw.exe"
  Delete "$INSTDIR\PptCOM.dll"

  File "${SRCDIR}\AnyThingDraw.exe"
  File "${SRCDIR}\PptCOM.dll"

  WriteUninstaller "$INSTDIR\Uninstall.exe"

  ; 注册卸载信息
  WriteRegStr HKLM "${UNINSTKEY}" "DisplayName" "${APPDISPLAY}"
  WriteRegStr HKLM "${UNINSTKEY}" "DisplayIcon" "$INSTDIR\AnyThingDraw.exe"
  WriteRegStr HKLM "${UNINSTKEY}" "DisplayVersion" "${APPVERSION}"
  WriteRegStr HKLM "${UNINSTKEY}" "Publisher" "${PUBLISHER}"
  WriteRegStr HKLM "${UNINSTKEY}" "URLInfoAbout" "https://draw.yfyw.top/"
  WriteRegStr HKLM "${UNINSTKEY}" "InstallLocation" "$INSTDIR"
  WriteRegStr HKLM "${UNINSTKEY}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKLM "${UNINSTKEY}" "QuietUninstallString" '"$INSTDIR\Uninstall.exe" /S'
  WriteRegDWORD HKLM "${UNINSTKEY}" "NoModify" 1
  WriteRegDWORD HKLM "${UNINSTKEY}" "NoRepair" 1
  WriteRegStr HKLM "Software\AnyThingDraw" "InstallDir" "$INSTDIR"

  ; 开始菜单快捷方式（桌面快捷方式由软件内选项自行创建）
  CreateDirectory "$SMPROGRAMS\AnyThingDraw"
  CreateShortCut "$SMPROGRAMS\AnyThingDraw\AnyThingDraw.lnk" "$INSTDIR\AnyThingDraw.exe"
  CreateShortCut "$SMPROGRAMS\AnyThingDraw\卸载 AnyThingDraw.lnk" "$INSTDIR\Uninstall.exe"
SectionEnd

Section "Uninstall"
  SetShellVarContext all

  nsExec::Exec 'taskkill /IM AnyThingDraw.exe /F'
  Pop $0
  Sleep 600

  Delete "$INSTDIR\AnyThingDraw.exe"
  Delete "$INSTDIR\PptCOM.dll"

  MessageBox MB_YESNO|MB_ICONQUESTION "是否同时删除配置、日志与用户数据？$\n（选择“否”将保留它们，便于日后重装继续使用）" IDNO keep_data
    RMDir /r "$INSTDIR\opt"
    RMDir /r "$INSTDIR\log"
    RMDir /r "$INSTDIR\AnyThingDraw"
    RMDir /r "$INSTDIR\installer"
keep_data:

  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"

  Delete "$SMPROGRAMS\AnyThingDraw\AnyThingDraw.lnk"
  Delete "$SMPROGRAMS\AnyThingDraw\卸载 AnyThingDraw.lnk"
  RMDir "$SMPROGRAMS\AnyThingDraw"

  DeleteRegKey HKLM "${UNINSTKEY}"
  DeleteRegKey HKLM "Software\AnyThingDraw"
SectionEnd
