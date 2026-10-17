#include "ATDrawOther.h"

#include "ATDrawConfiguration.h"

#include <io.h>
#include <objbase.h>
#include <psapi.h>
#include <shlobj.h>
#include <shlwapi.h>
#include <tlhelp32.h>
#pragma comment(lib, "shlwapi.lib")
#pragma comment(lib, "shell32.lib")

wstring GetCurrentExeDirectory()
{
	DWORD bufferSize = MAX_PATH;
	wstring buffer(bufferSize, L'\0');
	DWORD length = 0;

	while (true)
	{
		length = GetModuleFileNameW(NULL, &buffer[0], bufferSize);
		if (length == 0) return L"";
		else if (length < bufferSize)
		{
			buffer.resize(length);
			break;
		}
		else
		{
			bufferSize *= 2;
			buffer.resize(bufferSize, L'\0');
		}
	}

	filesystem::path fullPath(buffer);
	return fullPath.parent_path().wstring();
}
wstring GetCurrentExePath()
{
	DWORD bufferSize = MAX_PATH;
	wstring buffer(bufferSize, L'\0');
	DWORD length = 0;

	while (true)
	{
		length = GetModuleFileNameW(NULL, &buffer[0], bufferSize);
		if (length == 0) return L"";
		else if (length < bufferSize)
		{
			buffer.resize(length);
			break;
		}
		else
		{
			bufferSize *= 2;
			buffer.resize(bufferSize, L'\0');
		}
	}

	return buffer;
}
wstring GetCurrentExeName()
{
	DWORD bufferSize = MAX_PATH;
	wstring buffer(bufferSize, L'\0');
	DWORD length = 0;

	while (true)
	{
		length = GetModuleFileNameW(NULL, &buffer[0], bufferSize);
		if (length == 0) return L"";
		else if (length < bufferSize)
		{
			buffer.resize(length);
			break;
		}
		else
		{
			bufferSize *= 2;
			buffer.resize(bufferSize, L'\0');
		}
	}

	filesystem::path fullPath(buffer);
	return fullPath.filename().wstring();
}

//网络状态获取
// 提取指定模块中的资源文件
bool ExtractResource(LPCTSTR strDstFile, LPCTSTR strResType, LPCTSTR strResName)
{
	// 创建文件
	HANDLE hFile = ::CreateFile(strDstFile, GENERIC_WRITE, NULL, NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_TEMPORARY, NULL);
	if (hFile == INVALID_HANDLE_VALUE)
		return false;

	// 查找资源文件、加载资源到内存、得到资源大小
	HRSRC	hRes = ::FindResource(NULL, strResName, strResType);
	HGLOBAL	hMem = ::LoadResource(NULL, hRes);
	DWORD	dwSize = ::SizeofResource(NULL, hRes);

	// 写入文件
	DWORD dwWrite = 0;		// 返回写入字节
	::WriteFile(hFile, hMem, dwSize, &dwWrite, NULL);
	::CloseHandle(hFile);

	return true;
}

//判断id是否错乱
bool isValidString(const wstring& str)
{
	for (wchar_t ch : str)
	{
		// 如果字符不是可打印的，并且不是空格，则认为是乱码
		if (!iswprint(ch) && !iswspace(ch))  return false;
	}
	return true;
}
// 判断字符串中是否是合法 ASCII 字符
bool isAsciiPrintable(const wstring& input)
{
	for (wchar_t c : input)
		if (c < 32 || c > 126)
			return false;
	return true;
}

// 程序进程状态获取
bool isProcessRunning(const std::wstring& processPath)
{
	// 使用 try-catch 保护，防止非法路径字符导致 filesystem 崩溃
	try {
		// 预处理目标路径：自动处理双斜杠、相对路径等规范化问题
		filesystem::path targetPath = filesystem::weakly_canonical(processPath);

		PROCESSENTRY32W entry;
		entry.dwSize = sizeof(PROCESSENTRY32W);

		HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, NULL);
		if (snapshot == INVALID_HANDLE_VALUE) return false;

		if (Process32FirstW(snapshot, &entry)) {
			do {
				// 打开进程句柄
				HANDLE process = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, FALSE, entry.th32ProcessID);
				if (process == NULL) {
					continue;
				}

				// 获取进程完整路径
				wchar_t pathBuf[MAX_PATH];
				DWORD size = MAX_PATH;
				if (QueryFullProcessImageNameW(process, 0, pathBuf, &size)) {
					// 规范化当前遍历到的进程路径
					filesystem::path currentPath = filesystem::weakly_canonical(pathBuf);

					// 比较规范化后的路径（fs::path 的 == 在 Windows 下通常不区分大小写且理解路径结构）
					if (targetPath == currentPath) {
						CloseHandle(process);
						CloseHandle(snapshot);
						return true;
					}
				}

				CloseHandle(process);
			} while (Process32NextW(snapshot, &entry));
		}

		CloseHandle(snapshot);
	}
	catch (...) {
		// 如果发生任何路径转换异常，回退到安全状态
		return false;
	}

	return false;
}
// 进程程序路径查询
// 设置开机自启状态
bool SetStartupState(bool bAutoRun, wstring path, const wstring& nameclass)
{
	// 确保路径带有引号，处理带空格的路径
	if (path.empty() || path.front() != L'\"') {
		path = L"\"" + path + L"\"";
	}

	HKEY hKey;
	LPCWSTR lpRun = L"Software\\Microsoft\\Version\\Run"; // 注意：建议使用宏定义或常量

	// 打开注册表项
	long lRet = RegOpenKeyExW(HKEY_CURRENT_USER, L"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_WRITE, &hKey);
	if (lRet != ERROR_SUCCESS) return false;

	bool bResult = false;
	if (bAutoRun) {
		// 计算字节数：字符数 + 结束符，再乘以 sizeof(wchar_t)
		DWORD cbData = (DWORD)((path.length() + 1) * sizeof(wchar_t));
		lRet = RegSetValueExW(hKey, nameclass.c_str(), 0, REG_SZ, (const BYTE*)path.c_str(), cbData);
		bResult = (lRet == ERROR_SUCCESS);
	}
	else {
		lRet = RegDeleteValueW(hKey, nameclass.c_str());
		// 如果值本来就不存在，也可以视作成功
		bResult = (lRet == ERROR_SUCCESS || lRet == ERROR_FILE_NOT_FOUND);
	}

	RegCloseKey(hKey);
	return bResult;
}
// 查询开机自启状态
bool QueryStartupState(wstring path, const wstring& nameclass)
{
	HKEY hKey;
	long lRet = RegOpenKeyExW(HKEY_CURRENT_USER, L"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, KEY_READ, &hKey);
	if (lRet != ERROR_SUCCESS) return false;

	wchar_t regValue[MAX_PATH] = { 0 };
	DWORD dwType = 0;
	DWORD dwSize = sizeof(regValue); // 这里是字节数

	lRet = RegQueryValueExW(hKey, nameclass.c_str(), NULL, &dwType, (LPBYTE)regValue, &dwSize);
	RegCloseKey(hKey);

	if (lRet != ERROR_SUCCESS || dwType != REG_SZ) {
		return false;
	}

	// 处理带引号和不带引号的对比逻辑
	wstring strReg(regValue);
	wstring strPathWithQuotes = L"\"" + path + L"\"";

	// 只要注册表里的值包含我们的路径，或者完全相等
	return (_wcsicmp(regValue, path.c_str()) == 0 || _wcsicmp(regValue, strPathWithQuotes.c_str()) == 0);
}


// ---- 手写窗口实现的自定义 OK/Cancel 对话框：左「取消」右「确定」 ----
struct ATCustomDialogParams
{
	const wchar_t* title;
	const wchar_t* text;
	int result;
};
static LRESULT CALLBACK ATDialogWndProc(HWND h, UINT m, WPARAM w, LPARAM l)
{
	if (m == WM_CREATE)
	{
		CREATESTRUCTW* cs = reinterpret_cast<CREATESTRUCTW*>(l);
		SetWindowLongPtrW(h, GWLP_USERDATA, reinterpret_cast<LONG_PTR>(cs->lpCreateParams));
		return 0;
	}
	ATCustomDialogParams* p = reinterpret_cast<ATCustomDialogParams*>(GetWindowLongPtrW(h, GWLP_USERDATA));
	switch (m)
	{
	case WM_COMMAND:
		if (p)
		{
			if (LOWORD(w) == IDOK) { p->result = 1; DestroyWindow(h); return 0; }
			if (LOWORD(w) == IDCANCEL) { p->result = 0; DestroyWindow(h); return 0; }
		}
		break;
	case WM_CLOSE:
		if (p) p->result = 0;
		DestroyWindow(h);
		return 0;
	}
	return DefWindowProcW(h, m, w, l);
}
int ShowATOKCancelDialog(HWND owner, const wchar_t* text, const wchar_t* title)
{
	static bool registered = false;
	if (!registered)
	{
		WNDCLASSW wc = {};
		wc.lpfnWndProc = ATDialogWndProc;
		wc.hInstance = GetModuleHandleW(NULL);
		wc.hCursor = LoadCursorW(NULL, IDC_ARROW);
		wc.hbrBackground = reinterpret_cast<HBRUSH>(COLOR_BTNFACE + 1);
		wc.lpszClassName = L"ATCustomDialogClass";
		RegisterClassW(&wc);
		registered = true;
	}

	HDC dc = GetDC(NULL);
	int dpi = dc ? GetDeviceCaps(dc, LOGPIXELSX) : 96;
	if (dc) ReleaseDC(NULL, dc);
	auto S = [dpi](int v) { return MulDiv(v, dpi, 96); };

	RECT ro = {};
	if (owner) GetWindowRect(owner, &ro);
	int w = S(440), h = S(200);
	int x = ro.left + ((ro.right - ro.left) - w) / 2;
	int y = ro.top + ((ro.bottom - ro.top) - h) / 2;

	ATCustomDialogParams params = {};
	params.title = title;
	params.text = text;
	params.result = 0;

	HWND dlg = CreateWindowExW(WS_EX_DLGMODALFRAME, L"ATCustomDialogClass", title,
		WS_POPUP | WS_CAPTION | WS_SYSMENU, x, y, w, h, owner, NULL, GetModuleHandleW(NULL), &params);
	if (!dlg) return 0;

	HFONT font = static_cast<HFONT>(GetStockObject(DEFAULT_GUI_FONT));
	auto make = [&](const wchar_t* cls, const wchar_t* txt, DWORD style, int px, int py, int pw, int ph, int id) -> HWND
	{
		HWND c = CreateWindowExW(0, cls, txt, WS_CHILD | WS_VISIBLE | style,
			S(px), S(py), S(pw), S(ph), dlg, reinterpret_cast<HMENU>(static_cast<INT_PTR>(id)), GetModuleHandleW(NULL), NULL);
		if (c) SendMessageW(c, WM_SETFONT, reinterpret_cast<WPARAM>(font), TRUE);
		return c;
	};

	make(L"STATIC", text, SS_LEFT, 20, 18, 400, 90, 1000);
	HWND okBtn = make(L"BUTTON", L"确定", WS_TABSTOP | BS_DEFPUSHBUTTON, 250, 130, 90, 30, IDOK);
	make(L"BUTTON", L"取消", WS_TABSTOP | BS_PUSHBUTTON, 140, 130, 90, 30, IDCANCEL);

	if (owner) EnableWindow(owner, FALSE);
	ShowWindow(dlg, SW_SHOWNORMAL);
	UpdateWindow(dlg);
	if (okBtn) SetFocus(okBtn);

	while (IsWindow(dlg))
	{
		MSG msg;
		if (PeekMessageW(&msg, NULL, 0, 0, PM_REMOVE))
		{
			if (msg.message == WM_QUIT) break;
			TranslateMessage(&msg);
			DispatchMessageW(&msg);
		}
		else Sleep(5);
	}
	if (owner) EnableWindow(owner, TRUE);
	return params.result;
}
