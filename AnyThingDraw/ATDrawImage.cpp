#include "ATDrawImage.h"

//drawpad画笔
IMAGE alpha_drawpad(GetSystemMetrics(SM_CXSCREEN), GetSystemMetrics(SM_CYSCREEN)); //临时画板

int recall_image_recond, recall_image_reference;
shared_mutex RecallImageManipulatedSm;
chrono::high_resolution_clock::time_point RecallImageManipulated;

int RecallImagePeak = 0;
deque<RecallStruct> RecallImage;//撤回栈

//悬浮窗
IMAGE background(576, 386);
Graphics graphics(GetImageHDC(&background));

shared_mutex loadImageSm;
void atdrawLoadImage(IMAGE* pDstImg, LPCTSTR pImgFile, int nWidth, int nHeight, bool bResize)
{
	lock_guard loadImageLock(loadImageSm);
	loadimage(pDstImg, pImgFile, nWidth, nHeight, bResize);
}
void atdrawLoadImage(IMAGE* pDstImg, LPCTSTR pResType, LPCTSTR pResName, int nWidth, int nHeight, bool bResize)
{
	lock_guard loadImageLock(loadImageSm);
	loadimage(pDstImg, pResType, pResName, nWidth, nHeight, bResize);
}