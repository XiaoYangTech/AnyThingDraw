#pragma once
#include "ATDrawMain.h"

#include <tlhelp32.h> // 提供进程、模块、线程的遍历等功能

extern HWND floating_window; //悬浮窗窗口
extern HWND drawpad_window; //画板窗口
extern HWND ppt_window; //PPT控件窗口
extern HWND freeze_window; //定格背景窗口
extern HWND setting_window; //程序调测窗口

extern HWND ppt_show;
extern wstring ppt_title, ppt_software;

wstring GetWindowText(HWND hWnd);

struct ATDrawWindowsIsVisibleStruct
{
	ATDrawWindowsIsVisibleStruct()
	{
		floatingWindow = false;
		drawpadWindow = false;
		pptWindow = false;
		freezeWindow = false;

		allCompleted = false;
	}

	bool floatingWindow;
	bool drawpadWindow;
	bool pptWindow;
	bool freezeWindow;

	bool allCompleted;
};
extern ATDrawWindowsIsVisibleStruct ATDrawWindowsIsVisible;
extern bool rtsWait;
extern bool topWindowNow;

//置顶程序窗口
void TopWindow();