import AnyThingDraw.Thread.Status;

#include "ATDrawFreezeFrame.h"

#include "ATDrawConfiguration.h"
#include "ATDrawDisplayManagement.h"
#include "ATDrawDraw.h"
#include "ATDrawImage.h"
#include "ATDrawMagnification.h"
#include "ATDrawPlug-in.h"
#include "ATDrawSetting.h"
#include "ATDrawText.h"
#include "ATDrawWindow.h"


void FreezeFrameWindow()
{
	AnyThingDraw::Thread::StatusGuard guard("FreezeFrameWindow");

	DisableResizing(freeze_window, true);//禁止窗口拉伸
	SetWindowLong(freeze_window, GWL_STYLE, GetWindowLong(freeze_window, GWL_STYLE) & ~WS_CAPTION);//隐藏标题栏
	SetWindowPos(freeze_window, NULL, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOZORDER | SWP_DRAWFRAME);
	SetWindowLong(freeze_window, GWL_EXSTYLE, WS_EX_TOOLWINDOW);//隐藏任务栏

	IMAGE freeze_background, PptSign;
	if (setlist.regularSetting.avoidFullScreen)
	{
		freeze_background.Resize(MainMonitor.MonitorWidth, MainMonitor.MonitorHeight - 1);
		SetWindowPos(freeze_window, NULL, MainMonitor.rcMonitor.left, MainMonitor.rcMonitor.top, MainMonitor.MonitorWidth, MainMonitor.MonitorHeight - 1, SWP_NOZORDER | SWP_NOACTIVATE);
	}
	else
	{
		freeze_background.Resize(MainMonitor.MonitorWidth, MainMonitor.MonitorHeight);
		SetWindowPos(freeze_window, NULL, MainMonitor.rcMonitor.left, MainMonitor.rcMonitor.top, MainMonitor.MonitorWidth, MainMonitor.MonitorHeight, SWP_NOZORDER | SWP_NOACTIVATE);
	}
	SetImageColor(freeze_background, RGBA(0, 0, 0, 0), true);
	atdrawLoadImage(&PptSign, L"PNG", L"sign4");

	// 设置BLENDFUNCTION结构体
	BLENDFUNCTION blend;
	blend.BlendOp = AC_SRC_OVER;
	blend.BlendFlags = 0;
	blend.SourceConstantAlpha = 255; // 设置透明度，0为全透明，255为不透明
	blend.AlphaFormat = AC_SRC_ALPHA; // 使用源图像的alpha通道
	HDC hdcScreen = GetDC(NULL);
	// 调用UpdateLayeredWindow函数更新窗口
	POINT ptSrc = { 0,0 };
	SIZE sizeWnd = { freeze_background.getwidth(),freeze_background.getheight() };
	POINT ptDst = { 0,0 }; // 设置窗口位置
	UPDATELAYEREDWINDOWINFO ulwi = { 0 };
	ulwi.cbSize = sizeof(ulwi);
	ulwi.hdcDst = hdcScreen;
	ulwi.pptDst = &ptDst;
	ulwi.psize = &sizeWnd;
	ulwi.pptSrc = &ptSrc;
	ulwi.crKey = RGB(255, 255, 255);
	ulwi.pblend = &blend;
	ulwi.dwFlags = ULW_ALPHA;

	while (!(GetWindowLong(freeze_window, GWL_EXSTYLE) & WS_EX_LAYERED))
	{
		SetWindowLong(freeze_window, GWL_EXSTYLE, GetWindowLong(freeze_window, GWL_EXSTYLE) | WS_EX_LAYERED);
		if (GetWindowLong(freeze_window, GWL_EXSTYLE) & WS_EX_LAYERED) break;

		this_thread::sleep_for(chrono::milliseconds(10));
	}
	while (!(GetWindowLong(freeze_window, GWL_EXSTYLE) & WS_EX_NOACTIVATE))
	{
		SetWindowLong(freeze_window, GWL_EXSTYLE, GetWindowLong(freeze_window, GWL_EXSTYLE) | WS_EX_NOACTIVATE);
		if (GetWindowLong(freeze_window, GWL_EXSTYLE) & WS_EX_NOACTIVATE) break;

		this_thread::sleep_for(chrono::milliseconds(10));
	}
	// TODO 临时方案
	::SetWindowLong(freeze_window, GWL_EXSTYLE, ::GetWindowLong(freeze_window, GWL_EXSTYLE) | WS_EX_TRANSPARENT);

	ulwi.hdcSrc = GetImageHDC(&freeze_background);
	UpdateLayeredWindowIndirect(freeze_window, &ulwi);

	ATDrawWindowsIsVisible.freezeWindow = true;
	//ShowWindow(freeze_window, SW_SHOW);

	FreezeFrame.update = true;
	int wait = 0;
	bool show_freeze_window = false;

	while (!offSignal)
	{
		this_thread::sleep_for(chrono::milliseconds(20));

		if (magnificationReady)
		{
			if (FreezeFrame.mode == 1)
			{
				if (!show_freeze_window)
				{
					RequestUpdateMagWindow = 1;
					show_freeze_window = true;
				}

				while (!offSignal)
				{
					if (FreezeFrame.mode != 1 || PptInfoState.TotalPage != -1) break;


					this_thread::sleep_for(chrono::milliseconds(20));
				}

				if (PptInfoState.TotalPage != -1) FreezeFrame.mode = 0;
				FreezeFrame.update = true;
			}
			else if (show_freeze_window)
			{
				SetImageColor(freeze_background, RGBA(0, 0, 0, 0), true);
				ulwi.hdcSrc = GetImageHDC(&freeze_background);
				UpdateLayeredWindowIndirect(freeze_window, &ulwi);

				RequestUpdateMagWindow = 0;
				show_freeze_window = false;
			}
		}
		else if (FreezeFrame.mode == 1)
		{
			FreezeFrame.mode = 0;
			FreezeFrame.select = false;
		}

	}
}