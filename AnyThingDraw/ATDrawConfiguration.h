#pragma once
#include "ATDrawMain.h"

bool OccupyFileForRead(HANDLE* hFile, const wstring& filePath);
bool OccupyFileForWrite(HANDLE* hFile, const wstring& filePath);
bool UnOccupyFile(HANDLE* hFile);

struct SetListStruct
{
#pragma region 软件配置
	struct
	{
		ATDrawAtomic<bool> enable;
	}configurationSetting;
#pragma endregion

#pragma region 软件版本
	string updateArchitecture;
	bool enableAutoUpdate;
#pragma endregion

#pragma region 常规
	bool startUp;

	float settingGlobalScale;

	int topSleepTime;
	bool RightClickClose;
	bool BrushRecover, RubberRecover;

	struct
	{
		ATDrawAtomic<bool> moveRecover, clickRecover;

		ATDrawAtomic<bool> avoidFullScreen;
		ATDrawAtomic<int> teachingSafetyMode;
	}regularSetting;

#pragma endregion

#pragma region 绘制
	int paintDevice;
	ATDrawAtomic<bool> disableRTS;

	bool liftStraighten, waitStraighten;
	bool pointAdsorption;

	bool smoothWriting;
	// 双击或右键橡皮快速清空并切回批注
	bool eraserQuickClean;

	struct
	{
		int eraserMode; // 0压感粗细 1笔速粗细 2固定粗细
		int eraserSize;
	}eraserSetting;

	ATDrawAtomic<bool> hideTouchPointer;
#pragma endregion

#pragma region 保存
	struct
	{
		ATDrawAtomic<bool> enable;
		ATDrawAtomic<int> saveDays;
	}saveSetting;
#pragma endregion

#pragma region 性能
	struct
	{
		int preparationQuantity;
		ATDrawAtomic<int> drawpadFps;
		ATDrawAtomic<bool> superDraw;
	}performanceSetting;
#pragma endregion

#pragma region 预设
	struct
	{
		ATDrawAtomic<bool> memoryWidth;
		ATDrawAtomic<bool> memoryColor;

		ATDrawAtomic<bool> autoDefaultWidth;
		ATDrawAtomic<float> defaultBrush1Width;
		ATDrawAtomic<float> defaultHighlighter1Width;
	}presetSetting;
#pragma endregion

#pragma region 组件
	struct
	{
		// 快捷按钮
		struct
		{
			struct
			{
				// 应用
				ATDrawAtomic<bool> explorer;
				ATDrawAtomic<bool> taskmgr;
				ATDrawAtomic<bool> control;
			} appliance;
			struct
			{
				// 系统操作
				ATDrawAtomic<bool> desktop;
				ATDrawAtomic<bool> lockWorkStation;
			} system;
			struct
			{
				// 键盘模拟
				ATDrawAtomic<bool> keyboardesc;
				ATDrawAtomic<bool> keyboardAltF4;
			} keyboard;
		} shortcutButton;
	}component;
#pragma endregion

#pragma region 插件
	struct
	{
		bool createLnk, correctLnk;
	}shortcutAssistant;

	struct
	{
		struct
		{
			ATDrawAtomic<bool> enable;
			ATDrawAtomic<bool> indicator;
		}superTop;
	}plugInSetting;
#pragma endregion
};
extern SetListStruct setlist;
extern shared_mutex setlistUpdateMutex;
bool ReadSetting();
bool ReadSettingMini();
bool WriteSetting();

struct PptComSetListStruct
{
	PptComSetListStruct()
	{
		fixedHandWriting = true;
		memoryWidgetPosition = false;
		middlePageNumOpenOutline = false;
		exitShowOnFocusLost = true;
		allowWidgetDrag = false;

		showBottomBoth = true;
		showMiddleBoth = false;
		showBottomMiddle = true;

		bottomBothWidth = 0;
		bottomBothHeight = 0;
		middleBothWidth = 0;
		middleBothHeight = 0;
		bottomMiddleWidth = 0;
		bottomMiddleHeight = 0;

		bottomSideBothWidgetScale = 1.0f;
		bottomSideMiddleWidgetScale = 1.0f;
		middleSideBothWidgetScale = 1.0f;

		// autoKillWpsProcess = true;

		// 附加信息项
		setAdmin = false;
	}

	// 墨迹固定在对应页面上
	bool fixedHandWriting;
	// 显示加载画面
	// 记忆控件位置
	bool memoryWidgetPosition;
	// 点击中间页码打开大纲视图
	bool middlePageNumOpenOutline;
	// 切出放映窗口时自动结束放映
	bool exitShowOnFocusLost;
	// 是否允许控件拖动位置
	bool allowWidgetDrag;

	// 控件显示
	bool showBottomBoth;
	bool showMiddleBoth;
	bool showBottomMiddle;

	// 控件方位
	float bottomBothWidth;
	float bottomBothHeight;
	float middleBothWidth;
	float middleBothHeight;
	float bottomMiddleWidth;
	float bottomMiddleHeight;

	// 控件缩放
	float bottomSideBothWidgetScale;
	float bottomSideMiddleWidgetScale;
	float middleSideBothWidgetScale;

	// 自动结束未正确关闭的 WPP 进程
	// bool autoKillWpsProcess;

	// 附加信息项
	bool setAdmin;
};
extern PptComSetListStruct pptComSetlist;
bool PptComReadSetting();
bool PptComReadSettingPositionOnly();
bool PptComWriteSetting();

struct DdbInteractionSetListStruct
{
	DdbInteractionSetListStruct()
	{
		enable = false;
		runAsAdmin = false;

		DdbEdition = L"20261004a";
		DdbSHA256 = "791dc35c059dfe8099cea791fe245649f96bf9b62b1a05ba1dcc101df425ec33";

		// -----

		sleepTime = 500;

		mode = 1;
		hostPath = L"";
		restartHost = true;

		// -----

		intercept.SeewoWhiteboard3Floating = true;
		intercept.SeewoWhiteboard5Floating = true;
		intercept.SeewoWhiteboard5CFloating = true;
		intercept.SeewoPincoSideBarFloating = false;
		intercept.SeewoPincoDrawingFloating = true;
		intercept.SeewoPPTFloating = true;
		intercept.SeewoIwbAssistantFloating = true;
		intercept.YiouBoardFloating = true;
		intercept.AiClassFloating = true;
		intercept.ClassInXFloating = true;
		intercept.IntelligentClassFloating = true;
		intercept.ChangYanFloating = true;
		intercept.ChangYan5Floating = true;
		intercept.Iclass30SidebarFloating = false;
		intercept.Iclass30Floating = true;
		intercept.SeewoDesktopSideBarFloating = false;
		intercept.SeewoDesktopDrawingFloating = false;
	}

	bool enable;
	bool runAsAdmin;

	wstring DdbEdition;
	string DdbSHA256;

	// Ddb 配置文件

	int sleepTime;

	int mode; // 0 独立模式 1 随宿主程序和开启和关闭 2 随宿主程序关闭
	wstring hostPath;
	bool restartHost; // restartHost：（仅限独立模式）当宿主程序被关闭后，拦截到其他软件的窗口后，重启宿主程序

	// ----

	struct
	{
		bool SeewoWhiteboard3Floating;
		bool SeewoWhiteboard5Floating;
		bool SeewoWhiteboard5CFloating;
		bool SeewoPincoSideBarFloating;
		bool SeewoPincoDrawingFloating;
		bool SeewoPPTFloating;
		bool SeewoIwbAssistantFloating;
		bool YiouBoardFloating;
		bool AiClassFloating;
		bool ClassInXFloating;
		bool IntelligentClassFloating;
		bool ChangYanFloating;
		bool ChangYan5Floating;
		bool Iclass30SidebarFloating;
		bool Iclass30Floating;
		bool SeewoDesktopSideBarFloating;
		bool SeewoDesktopDrawingFloating;
	} intercept;
};
extern DdbInteractionSetListStruct ddbInteractionSetList;
//bool DdbReadInteraction();
bool DdbWriteInteraction(bool change, bool close);

bool GetMemory();
bool SetMemory();
