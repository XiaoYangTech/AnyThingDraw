#pragma once
#include "ATDrawMain.h"



struct ATDrawSysVersionStruct
{
	int majorVersion;
	int	minorVersion;
	int buildNumber;
};

typedef LONG(WINAPI* RtlGetVersionPtr)(RTL_OSVERSIONINFOW*);
ATDrawSysVersionStruct GetWindowsVersion();