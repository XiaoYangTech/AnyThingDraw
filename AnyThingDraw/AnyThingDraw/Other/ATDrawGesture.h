#pragma once

#include "../../ATDrawMain.h"

class ATDrawGesture
{
private:
	ATDrawGesture() = delete;

public:
	static BOOL DisableEdgeGestures(HWND hwnd, BOOL disable);
};