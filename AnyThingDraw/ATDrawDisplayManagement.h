/*
 * @file		ATDrawDisplayManagement.h
 * @brief		AnyThingDraw Display management | 显示器管理
 * @note		Obtain and manage display status | 获取并管理显示器状态
 *
 * @author		AlanCRL
 * @qq			2685549821
 * @email		alan-crl@foxmail.com
 * @modify		InspireWorks（亿方运维）自 2026 年起修改（基于智绘教 Inkeys，GPL-3.0）
*/

// All function and variable descriptions should be in the corresponding cpp file.
// 所有的函数和变量说明应该在对应的 cpp 文件中。

#pragma once
#include "ATDrawMain.h"

extern ATDrawAtomic<int> DisplaysNumber;

class EDIDInfoStruct
{
public:
	EDIDInfoStruct() {};
	EDIDInfoStruct(bool validTarget, wstring edidVersionTarget, wstring deviceIDTarget)
	{
		valid = validTarget;
		edidVersion = edidVersionTarget;
		deviceID = deviceIDTarget;
	}

public:
	bool operator==(const EDIDInfoStruct& other) const
	{
		return valid == other.valid &&
			edidVersion == other.edidVersion &&
			deviceID == other.deviceID;
	}
	bool operator!=(const EDIDInfoStruct& other) const
	{
		return !(*this == other);
	}

public:
	bool valid;
	wstring edidVersion;
	wstring deviceID;
};

class MonitorInfoStruct
{
public:
	MonitorInfoStruct() {};
	MonitorInfoStruct(HMONITOR MonitorTarget, RECT rcMonitorTarget, int MonitorWidthTarget, int MonitorHeightTarget, EDIDInfoStruct edidInfoTarget, int MonitorPhyWidthTarget, int MonitorPhyHeightTarget, int MonitorPhyRawWidthTarget, int MonitorPhyRawHeightTarget, int displayOrientationTarget, bool isMainMonitorTarget)
	{
		Monitor = MonitorTarget;
		rcMonitor = rcMonitorTarget;
		MonitorWidth = MonitorWidthTarget;
		MonitorHeight = MonitorHeightTarget;
		edidInfo = edidInfoTarget;
		MonitorPhyWidth = MonitorPhyWidthTarget;
		MonitorPhyHeight = MonitorPhyHeightTarget;
		MonitorPhyRawWidth = MonitorPhyRawWidthTarget;
		MonitorPhyRawHeight = MonitorPhyRawHeightTarget;
		displayOrientation = displayOrientationTarget;

		isMainMonitor = isMainMonitorTarget;
	}

public:
	bool operator==(const MonitorInfoStruct& other) const
	{
		return Monitor == other.Monitor &&
			EqualRect(&rcMonitor, &other.rcMonitor) &&
			MonitorWidth == other.MonitorWidth &&
			MonitorHeight == other.MonitorHeight &&
			edidInfo == other.edidInfo &&
			MonitorPhyWidth == other.MonitorPhyWidth &&
			MonitorPhyHeight == other.MonitorPhyHeight &&
			MonitorPhyRawWidth == other.MonitorPhyRawWidth &&
			MonitorPhyRawHeight == other.MonitorPhyRawHeight &&
			displayOrientation == other.displayOrientation;
	}
	bool operator!=(const MonitorInfoStruct& other) const
	{
		return !(*this == other);
	}

public:
	HMONITOR Monitor;
	RECT rcMonitor;
	ATDrawAtomic<int> MonitorWidth;
	ATDrawAtomic<int> MonitorHeight;
	EDIDInfoStruct edidInfo;
	ATDrawAtomic<int> MonitorPhyRawWidth;
	ATDrawAtomic<int> MonitorPhyRawHeight;
	ATDrawAtomic<int> MonitorPhyWidth;
	ATDrawAtomic<int> MonitorPhyHeight;
	ATDrawAtomic<int> displayOrientation;

public:
	bool isMainMonitor;
};
extern vector<MonitorInfoStruct> MonitorInfo;
extern shared_mutex DisplaysInfoSm;

extern MonitorInfoStruct MainMonitor;

bool ATDrawGetModelDriverFromDeviceID(LPCWSTR lpDeviceID, wstring& model, wstring& driver);
bool ATDrawIsCorrectEDID(const BYTE* pEDIDBuf, DWORD dwcbBufSize, LPCWSTR lpModel);
bool ATDrawGetDeviceEDID(LPCWSTR lpModel, LPCWSTR lpDriver, BYTE* pDataBuf, DWORD dwcbBufSize, DWORD* pdwGetBytes);

void DisplayManagementMain();