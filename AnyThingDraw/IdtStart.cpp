#include "IdtStart.h"

#include "IdtDisplayManagement.h"
#include "IdtUpdate.h"


// 分辨率不合适、内存不合适、系统低于win10


IdtSysVersionStruct GetWindowsVersion()
{
	IdtSysVersionStruct ret = { 0,0,0 };

	// 动态加载 ntdll.dll 并获取 RtlGetVersion 函数地址
	HMODULE hMod = GetModuleHandleW(L"ntdll.dll");
	if (hMod)
	{
		RtlGetVersionPtr pRtlGetVersion = (RtlGetVersionPtr)GetProcAddress(hMod, "RtlGetVersion");
		if (pRtlGetVersion)
		{
			// 创建并初始化 RTL_OSVERSIONINFOW 结构体
			RTL_OSVERSIONINFOW rovi = { 0 };
			rovi.dwOSVersionInfoSize = sizeof(rovi);
			// 调用 RtlGetVersion 获取系统版本信息
			if (pRtlGetVersion(&rovi) == 0)
			{
				ret.majorVersion = static_cast<int>(rovi.dwMajorVersion);
				ret.minorVersion = static_cast<int>(rovi.dwMinorVersion);
				ret.buildNumber = static_cast<int>(rovi.dwBuildNumber);
			}
		}
	}

	return ret;
}