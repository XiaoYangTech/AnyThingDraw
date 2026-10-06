#include "ATDrawTime.h"

//时间戳
wstring getTimestamp()
{
	auto now = std::chrono::system_clock::now();
	auto duration = now.time_since_epoch();
	auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(duration).count();
	std::wstringstream wss;
	wss << millis;
	return wss.str();
}
//获取日期
wstring CurrentDate()
{
	auto t = std::time(nullptr);
	auto tm = *std::localtime(&t);
	std::wostringstream woss;
	woss << std::put_time(&tm, L"%Y-%m-%d");
	return woss.str();
}
//获取时间
wstring CurrentTime()
{
	auto t = std::time(nullptr);
	auto tm = *std::localtime(&t);
	std::wostringstream woss;
	woss << std::put_time(&tm, L"%H-%M-%S");
	return woss.str();
}
