#pragma once
#include "IdtMain.h"



struct IdtSysVersionStruct
{
	int majorVersion;
	int	minorVersion;
	int buildNumber;
};

typedef LONG(WINAPI* RtlGetVersionPtr)(RTL_OSVERSIONINFOW*);
IdtSysVersionStruct GetWindowsVersion();