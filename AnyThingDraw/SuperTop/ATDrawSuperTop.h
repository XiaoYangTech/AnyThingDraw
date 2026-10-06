#pragma once

#include "../ATDrawMain.h"

bool hasUiAccess(HANDLE tok);
void SurperTopMain(wstring lpCmdLine);

extern ATDrawAtomic<bool> hasSuperTop;
void LaunchSurperTop(wstring cmdLine);