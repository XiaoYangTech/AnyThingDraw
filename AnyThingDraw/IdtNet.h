#pragma once

#include <string>
#include <atomic>

std::string GetAppUpdateInformation(std::string os, std::string arch, std::string version);
bool DownloadEdition(std::string domain, std::string path, std::wstring directory, std::wstring fileName, std::atomic_ullong& downloadedSize, std::string referer = "");
bool ReportDevicePing(std::string deviceKey, std::string deviceName);