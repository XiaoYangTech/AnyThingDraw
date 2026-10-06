#include "ATDrawHistoricalDrawpad.h"

#include "ATDrawConfiguration.h"
#include "ATDrawDisplayManagement.h"
#include "ATDrawDraw.h"
#include "ATDrawDrawpad.h"
#include "ATDrawFloating.h"
#include "ATDrawFreezeFrame.h"
#include "ATDrawImage.h"
#include "ATDrawMagnification.h"
#include "ATDrawState.h"
#include "ATDrawText.h"
#include "ATDrawTime.h"
#include "ATDrawWindow.h"

int current_record_pointer, total_record_pointer;
int reference_record_pointer, practical_total_record_pointer;
Json::Value record_value;

// 载入记录
// 保存图像到指定目录
// 撤回操作
void ATDrawRecall()
{
	// 标识绘制等待
	{
		unique_lock<shared_mutex> LockdrawWaitingSm(drawWaitingSm);
		drawWaiting = true;
		LockdrawWaitingSm.unlock();
	}
	// 防止绘图时撤回冲突
	{
		std::shared_lock<std::shared_mutex> LockStrokeImageListSm(StrokeImageListSm);
		bool start = !StrokeImageList.empty();
		LockStrokeImageListSm.unlock();

		//正在绘制则取消操作
		if (start)
		{
			// 取消标识绘制等待
			{
				unique_lock<shared_mutex> LockdrawWaitingSm(drawWaitingSm);
				drawWaiting = false;
				LockdrawWaitingSm.unlock();
			}
			return;
		}
	}

	pair<int, int> tmp_recond = make_pair(0, 0);
	int tmp_recall_image_type = 0;
	if (!RecallImage.empty())
	{
		tmp_recond = RecallImage.back().recond;
		tmp_recall_image_type = RecallImage.back().type;

		if (RecallImage.back().type == 2 && stateMode.StateModeSelect != StateModeSelectEnum::ATDrawSelection && !CompareImagesWithBuffer(&drawpad, &RecallImage.back().img));
		else RecallImage.pop_back();
		deque<RecallStruct>(RecallImage).swap(RecallImage); // 使用swap技巧来释放未使用的内存
	}

	if (!RecallImage.empty())
	{
		drawpad = RecallImage.back().img;
		extreme_point = RecallImage.back().extreme_point;
		recall_image_recond = RecallImage.back().recond.first;
	}
	else
	{

		SetImageColor(drawpad, RGBA(0, 0, 0, 0), true);
		extreme_point.clear();
		recall_image_recond = 0;
		FirstDraw = true;
	}
	SetImageColor(window_background, RGBA(0, 0, 0, 1), true);
	hiex::TransparentImage(&window_background, 0, 0, &drawpad);

	if (stateMode.StateModeSelect != StateModeSelectEnum::ATDrawSelection)
	{
		// 设置BLENDFUNCTION结构体
		BLENDFUNCTION blend;
		blend.BlendOp = AC_SRC_OVER;
		blend.BlendFlags = 0;
		blend.SourceConstantAlpha = 255; // 设置透明度，0为全透明，255为不透明
		blend.AlphaFormat = AC_SRC_ALPHA; // 使用源图像的alpha通道
		HDC hdcScreen = GetDC(NULL);
		// 调用UpdateLayeredWindow函数更新窗口
		POINT ptSrc = { 0,0 };
		SIZE sizeWnd = { drawpad.getwidth(),drawpad.getheight() };
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

		// 定义要更新的矩形区域
		ulwi.hdcSrc = GetImageHDC(&window_background);
		UpdateLayeredWindowIndirect(drawpad_window, &ulwi);
	}
	else
	{
		reserve_drawpad = true;

		ChangeStateModeToPen();
	}

	// 取消标识绘制等待
	{
		unique_lock<shared_mutex> LockdrawWaitingSm(drawWaitingSm);
		drawWaiting = false;
		LockdrawWaitingSm.unlock();
	}
	return;
}
