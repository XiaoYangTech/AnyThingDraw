#pragma once
#include "ATDrawMain.h"

//drawpad画笔
extern IMAGE alpha_drawpad; //临时画板
extern IMAGE tester; //图形绘制画板
extern IMAGE pptdrawpad; //PPT控件画板

extern int recall_image_recond, recall_image_reference;
extern shared_mutex RecallImageManipulatedSm;
extern chrono::high_resolution_clock::time_point RecallImageManipulated;
struct RecallStruct
{
	IMAGE img;
	std::map<std::pair<int, int>, bool> extreme_point;
	int type;
	pair<int, int> recond;
};
extern int RecallImagePeak;
extern deque<RecallStruct> RecallImage;//撤回栈

//悬浮窗
extern IMAGE background;
extern Graphics graphics;


extern shared_mutex loadImageSm;
void atdrawLoadImage(IMAGE* pDstImg, LPCTSTR pImgFile, int nWidth = 0, int nHeight = 0, bool bResize = false);
void atdrawLoadImage(IMAGE* pDstImg, LPCTSTR pResType, LPCTSTR pResName, int nWidth = 0, int nHeight = 0, bool bResize = false);