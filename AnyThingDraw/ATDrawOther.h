#pragma once
#include "ATDrawMain.h"
#include "ATDrawText.h"

wstring GetCurrentExeDirectory();
wstring GetCurrentExePath();
wstring GetCurrentExeName();

bool ExtractResource(LPCTSTR strDstFile, LPCTSTR strResType, LPCTSTR strResName);

bool isValidString(const wstring& str);
bool isAsciiPrintable(const wstring& input);

bool isProcessRunning(const std::wstring& processPath);

bool SetStartupState(bool bAutoRun, wstring path, const wstring& nameclass);
bool QueryStartupState(wstring path, const wstring& nameclass);