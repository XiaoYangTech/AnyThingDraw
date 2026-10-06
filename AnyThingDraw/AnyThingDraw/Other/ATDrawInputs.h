#pragma once

#include "../../ATDrawMain.h"

class ATDrawInputs
{
private:
	ATDrawInputs() = delete;

public:
	static void SetKeyBoardDown(BYTE key, bool down);
	static bool IsKeyBoardDown(BYTE key);

	static void* downMap;
};