#include "ATDrawUpdate.h"

#include "ATDrawConfiguration.h"
#include "ATDrawOther.h"
#include "ATDrawSetting.h"
#include "ATDrawText.h"
#include "ATDrawTime.h"
#include "ATDrawWindow.h"
#include "ATDrawNet.h"

// 程序自动更新

bool mandatoryUpdate; // 强制更新符号
bool inconsistentArchitecture;
AutomaticUpdateStateEnum AutomaticUpdateState;
namespace
{
	struct UpdateTargetSnapshot
	{
		string channel;
		string architecture;
		bool enableAutoUpdate;
	};

	UpdateTargetSnapshot GetUpdateTargetSnapshot()
	{
		shared_lock<shared_mutex> lock(setlistUpdateMutex);
		return { setlist.UpdateChannel, setlist.updateArchitecture, setlist.enableAutoUpdate };
	}

	void SetUpdateChannelSnapshot(const string& channel)
	{
		unique_lock<shared_mutex> lock(setlistUpdateMutex);
		setlist.UpdateChannel = channel;
	}
}
wstring get_domain_name(wstring url) {
	wregex pattern(L"([a-zA-z]+://[^/]+)");
	wsmatch match;
	if (regex_search(url, match, pattern)) return match[0].str();
	else return L"";
}
wstring convertToHttp(const wstring& url)
{
	//更新保险
	//if (getCurrentDate() >= L"20231020") return url;

	wstring httpPrefix = L"http://";
	if (url.length() >= 7 && url.compare(0, 7, httpPrefix) == 0) return url;
	else if (url.length() >= 8 && url.compare(0, 8, L"https://") == 0) return httpPrefix + url.substr(8);
	else return httpPrefix + url;
}

string GetRefererInfo()
{
	string ret;
	UpdateTargetSnapshot updateTarget = GetUpdateTargetSnapshot();
	ret += utf16ToUtf8(editionDate) + ",";
	ret += utf16ToUtf8(programArchitecture) + ",";
	ret += updateTarget.channel + ",";
	ret += updateTarget.enableAutoUpdate ? "true," : "false,";
	ret += utf16ToUtf8(windowsEdition);
	return ret;
}

std::wstring latestDownloadUrl;

static bool IsNewerVersion(const std::wstring& latest, const std::wstring& current)
{
	auto splitVer = [](const std::wstring& v) -> std::vector<long long>
		{
			std::vector<long long> out;
			std::wstring cur;
			std::wstring s = v;
			if (!s.empty() && (s[0] == L'v' || s[0] == L'V')) s = s.substr(1);
			for (wchar_t c : s)
			{
				if (c >= L'0' && c <= L'9') cur += c;
				else if (!cur.empty()) { try { out.push_back(std::stoll(cur)); } catch (...) {} cur.clear(); }
			}
			if (!cur.empty()) { try { out.push_back(std::stoll(cur)); } catch (...) {} }
			return out;
		};
	auto av = splitVer(latest), bv = splitVer(current);
	for (size_t i = 0; i < max(av.size(), bv.size()); i++)
	{
		long long x = i < av.size() ? av[i] : 0, y = i < bv.size() ? bv[i] : 0;
		if (x > y) return true;
		if (x < y) return false;
	}
	return false;
}

EditionInfoClass GetEditionInfo(string channel, string arch)
{
	/*
	* 错误码：
	* 1 下载失败
	* 2 下载信息损坏
	* 3 下载信息不符合规范
	* 200 下载信息成功
	*/
	EditionInfoClass retEditionInfo;

	// 内部架构标识映射到亿方智云处理器标识
	string apiArch = "ia32";
	if (arch == "win64") apiArch = "x64";
	else if (arch == "arm64") apiArch = "arm64";

	string editionInformation = GetAppUpdateInformation("win32", apiArch, utf16ToUtf8(editionDate));
	if (editionInformation == "Error")
	{
		retEditionInfo.errorCode = 1;
		return retEditionInfo;
	}

	istringstream jsonContentStream(editionInformation);
	Json::CharReaderBuilder readerBuilder;
	Json::Value root;
	string jsonErr;
	if (!Json::parseFromStream(readerBuilder, jsonContentStream, &root, &jsonErr))
	{
		retEditionInfo.errorCode = 2;
		return retEditionInfo;
	}

	if (!(root.isMember("ok") && root["ok"].isBool() && root["ok"].asBool() && root.isMember("data") && root["data"].isObject()))
	{
		retEditionInfo.errorCode = 3;
		return retEditionInfo;
	}

	Json::Value& data = root["data"];
	if (!(data.isMember("latest_version") && data["latest_version"].isString()))
	{
		retEditionInfo.errorCode = 3;
		return retEditionInfo;
	}

	retEditionInfo.editionDate = utf8ToUtf16(data["latest_version"].asString());
	if (data.isMember("changelog") && data["changelog"].isString()) retEditionInfo.explain = utf8ToUtf16(data["changelog"].asString());
	if (data.isMember("page_url") && data["page_url"].isString()) retEditionInfo.pageUrl = utf8ToUtf16(data["page_url"].asString());
	if (data.isMember("has_update") && data["has_update"].isBool()) retEditionInfo.hasUpdate = data["has_update"].asBool();

	if (data.isMember("download_url") && data["download_url"].isString())
	{
		string downloadUrl = data["download_url"].asString();
		if (!downloadUrl.empty())
		{
			size_t lastSlash = downloadUrl.find_last_of('/');
			string fileName = (lastSlash != string::npos) ? downloadUrl.substr(lastSlash + 1) : "AnyThingDrawSetup.exe";
			retEditionInfo.representation = utf8ToUtf16(fileName);
			retEditionInfo.path[0] = downloadUrl;
			retEditionInfo.path_size = 1;
		}
	}

	if (data.isMember("matched") && data["matched"].isObject())
	{
		Json::Value& matched = data["matched"];
		if (matched.isMember("sha256") && matched["sha256"].isString()) retEditionInfo.hash_sha256 = matched["sha256"].asString();
		if (matched.isMember("size_bytes") && matched["size_bytes"].isUInt64()) retEditionInfo.fileSize = matched["size_bytes"].asUInt64();
	}

	retEditionInfo.channel = "LTS";
	retEditionInfo.errorCode = 200;

	// 手动更新按钮地址：优先更新页，其次安装包直链
	if (!retEditionInfo.pageUrl.empty()) latestDownloadUrl = retEditionInfo.pageUrl;
	else if (retEditionInfo.path_size > 0 && !retEditionInfo.path[0].empty()) latestDownloadUrl = utf8ToUtf16(retEditionInfo.path[0]);

	return retEditionInfo;
}
DownloadNewProgramStateClass downloadNewProgramState;

void splitUrl(string input_url, string& prefix, string& domain, string& path)
{
	// 更新后的正则表达式，捕获前缀，并要求域名中至少包含一个点
	regex url_regex(R"(^\s*(?:([a-zA-Z]+://))?((?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?::\d+)?)(/\S*)?\s*$)", regex::icase);
	smatch url_match_result;

	if (regex_match(input_url, url_match_result, url_regex))
	{
		prefix = url_match_result[1].matched ? url_match_result[1].str() : "";
		domain = url_match_result[2].str();
		path = url_match_result[3].matched ? url_match_result[3].str() : "";
	}
	else
	{
		prefix.clear();
		domain.clear();
		path.clear();
	}
}
AutomaticUpdateStateEnum DownloadNewProgram(DownloadNewProgramStateClass* state, EditionInfoClass editionInfo, string url, string arch)
{
	using enum AutomaticUpdateStateEnum;

	error_code ec;
	if (_waccess((globalPath + L"installer").c_str(), 4) == 0)
	{
		filesystem::remove_all(globalPath + L"installer", ec);
		filesystem::create_directory(globalPath + L"installer", ec);
	}
	else filesystem::create_directory(globalPath + L"installer", ec);

	string prefix, domain, path;
	splitUrl(url, prefix, domain, path);

	state->downloadedSize.store(0);
	state->fileSize.store(editionInfo.fileSize.load());

	wstring timestamp = getTimestamp();
	bool reslut = DownloadEdition(domain, path, globalPath + L"installer\\", L"new_procedure_" + timestamp + L".tmp", state->downloadedSize, GetRefererInfo());

	if (reslut)
	{
		error_code ec;
		filesystem::remove(globalPath + L"installer\\new_procedure_" + timestamp + L".exe", ec);
		filesystem::remove(globalPath + L"installer\\" + editionInfo.representation, ec);

		filesystem::rename(globalPath + L"installer\\new_procedure_" + timestamp + L".tmp", globalPath + L"installer\\new_procedure_" + timestamp + L".zip", ec);
		if (ec) return UpdateDownloadDamage;

		HZIP hz = OpenZip((globalPath + L"installer\\new_procedure_" + timestamp + L".zip").c_str(), 0);
		SetUnzipBaseDir(hz, (globalPath + L"installer").c_str());
		ZIPENTRY ze;
		GetZipItem(hz, -1, &ze);
		int numitems = ze.index;
		for (int i = 0; i < numitems; i++)
		{
			GetZipItem(hz, i, &ze);
			UnzipItem(hz, i, ze.name);
		}
		CloseZip(hz);

		filesystem::remove(globalPath + L"installer\\new_procedure_" + timestamp + L".zip", ec);
		filesystem::rename(globalPath + L"installer\\" + editionInfo.representation, globalPath + L"installer\\new_procedure_" + timestamp + L".exe", ec);
		if (ec) return UpdateDownloadDamage;

		string hash_md5, hash_sha256;
		{
			hashwrapper* myWrapper = new md5wrapper();
			hash_md5 = myWrapper->getHashFromFileW(globalPath + L"installer\\new_procedure_" + timestamp + L".exe");
			delete myWrapper;
		}
		{
			hashwrapper* myWrapper = new sha256wrapper();
			hash_sha256 = myWrapper->getHashFromFileW(globalPath + L"installer\\new_procedure_" + timestamp + L".exe");
			delete myWrapper;
		}

		//创建 update.json 文件，指示更新
		if (editionInfo.hash_md5 == hash_md5 && editionInfo.hash_sha256 == hash_sha256)
		{
			if (!GetUpdateTargetSnapshot().enableAutoUpdate && !mandatoryUpdate)
			{
				error_code ec;
				filesystem::remove(globalPath + L"installer\\new_procedure_" + timestamp + L".exe", ec);

				return UpdateNew;
			}
			else
			{
				Json::Value root;

				root["edition"] = Json::Value(utf16ToUtf8(editionInfo.editionDate));
				root["path"] = Json::Value("installer\\new_procedure_" + utf16ToUtf8(timestamp) + ".exe");
				root["representation"] = Json::Value("new_procedure_" + utf16ToUtf8(timestamp) + ".exe");
				root["channel"] = Json::Value(editionInfo.channel);

				root["hash"]["md5"] = Json::Value(editionInfo.hash_md5);
				root["hash"]["sha256"] = Json::Value(editionInfo.hash_sha256);

				root["arch"] = Json::Value(arch);

				root["old_name"] = Json::Value(utf16ToUtf8(GetCurrentExeName()));
				if (mandatoryUpdate) root["MandatoryUpdate"] = Json::Value(mandatoryUpdate);

				Json::StreamWriterBuilder outjson;
				outjson.settings_["emitUTF8"] = true;
				unique_ptr<Json::StreamWriter> writer(outjson.newStreamWriter());
				ofstream writejson(globalPath + L"installer\\update.json", ios::binary);
				writejson << "\xEF\xBB\xBF";
				writer->write(root, &writejson);
				writejson.close();
			}
		}
		else
		{
			error_code ec;
			filesystem::remove(globalPath + L"installer\\new_procedure_" + timestamp + L".exe", ec);

			return UpdateDownloadDamage;
		}
	}
	else return UpdateDownloadFail;

	return UpdateRestart;
}

AutomaticUpdateStateEnum DownloadNewInstaller(DownloadNewProgramStateClass* state, EditionInfoClass editionInfo, string url, string arch)
{
	using enum AutomaticUpdateStateEnum;

	error_code ec;
	if (_waccess((globalPath + L"installer").c_str(), 4) == 0)
	{
		filesystem::remove_all(globalPath + L"installer", ec);
		filesystem::create_directory(globalPath + L"installer", ec);
	}
	else filesystem::create_directory(globalPath + L"installer", ec);

	string prefix, domain, path;
	splitUrl(url, prefix, domain, path);
	if (domain.empty()) return UpdateDownloadFail;

	state->downloadedSize.store(0);
	state->fileSize.store(editionInfo.fileSize.load());

	wstring timestamp = getTimestamp();
	wstring tmpFile = L"atdraw_setup_" + timestamp + L".tmp";
	wstring exeFile = L"atdraw_setup_" + timestamp + L".exe";

	if (!DownloadEdition(domain, path, globalPath + L"installer\\", tmpFile, state->downloadedSize, GetRefererInfo()))
		return UpdateDownloadFail;

	filesystem::remove(globalPath + L"installer\\" + exeFile, ec);
	filesystem::rename(globalPath + L"installer\\" + tmpFile, globalPath + L"installer\\" + exeFile, ec);
	if (ec) return UpdateDownloadDamage;

	// 云端提供了校验值 / 大小时校验安装包
	if (!editionInfo.hash_sha256.empty())
	{
		hashwrapper* myWrapper = new sha256wrapper();
		string hash_sha256 = myWrapper->getHashFromFileW(globalPath + L"installer\\" + exeFile);
		delete myWrapper;
		if (hash_sha256 != editionInfo.hash_sha256)
		{
			filesystem::remove(globalPath + L"installer\\" + exeFile, ec);
			return UpdateDownloadDamage;
		}
	}
	if (editionInfo.fileSize.load() > 0 && state->downloadedSize.load() != editionInfo.fileSize.load())
	{
		filesystem::remove(globalPath + L"installer\\" + exeFile, ec);
		return UpdateDownloadDamage;
	}

	// 启动 NSIS 安装程序：/S 静默安装，/D 指定当前安装目录（必须是最后一个参数、不加引号）
	// 安装程序自行请求 UAC 提权，安装完成后会自动重新启动本软件
	wstring installDir = globalPath;
	while (!installDir.empty() && installDir.back() == L'\\') installDir.pop_back();
	wstring parameters = L"/S /D=" + installDir;

	SHELLEXECUTEINFOW sei = { 0 };
	sei.cbSize = sizeof(sei);
	sei.fMask = SEE_MASK_NOCLOSEPROCESS;
	sei.lpVerb = L"open";
	sei.lpFile = (globalPath + L"installer\\" + exeFile).c_str();
	sei.lpParameters = parameters.c_str();
	sei.nShow = SW_SHOWNORMAL;
	if (!ShellExecuteExW(&sei)) return UpdateDownloadDamage;

	// 给安装程序留出弹 UAC 的时间，随后退出本程序以便覆盖安装
	if (sei.hProcess) { WaitForSingleObject(sei.hProcess, 1500); CloseHandle(sei.hProcess); }

	AutomaticUpdateState = UpdateRestart;

	// 通知主循环退出，让安装程序接管覆盖安装
	offSignal = 1;

	return UpdateRestart;
}

bool isWindows8OrGreater;
wstring windowsEdition;
ATDrawAtomic<int> downloadLine = 1;

void AutomaticUpdate()
{
	bool state = true;
	bool update = true;

	bool against = false;
	int updateTimes = 0;

	UpdateTargetSnapshot updateTarget = GetUpdateTargetSnapshot();
	string updateArch = updateTarget.architecture;

	EditionInfoClass editionInfo;
	using enum AutomaticUpdateStateEnum;

updateStart:
	for (updateTimes = 0; !offSignal && updateTimes < 3; updateTimes++)
	{
		AutomaticUpdateState = UpdateObtainInformation;

		state = true;
		against = false;

		updateTarget = GetUpdateTargetSnapshot();
		updateArch = updateTarget.architecture;

		//获取最新版本信息
		if (state)
		{
			editionInfo = GetEditionInfo(updateTarget.channel, updateArch);

			if (editionInfo.errorCode != 200)
			{
				state = false, against = true;
				if (editionInfo.errorCode == 1) AutomaticUpdateState = UpdateInformationFail;
				else if (editionInfo.errorCode == 2) AutomaticUpdateState = UpdateInformationDamage;
				else AutomaticUpdateState = UpdateInformationUnStandardized;
			}
			else if (updateTarget.channel != editionInfo.channel)
			{
				SetUpdateChannelSnapshot(editionInfo.channel);
				WriteSetting();
			}
		}

		//下载最新版本
		if (state && editionInfo.editionDate != L"" && ((IsNewerVersion(editionInfo.editionDate, editionDate) && GetUpdateTargetSnapshot().enableAutoUpdate) || mandatoryUpdate))
		{
			if (editionInfo.path_size > 0 && !editionInfo.path[0].empty())
			{
				// 亿方智云按架构返回了 NSIS 安装包：下载并启动安装程序
				AutomaticUpdateState = DownloadNewInstaller(&downloadNewProgramState, editionInfo, editionInfo.path[0], updateArch);
				state = false;
			}
			else
			{
				// 云端暂无匹配当前处理器的安装包：提示新版本，由用户点击"手动更新"打开更新页
				AutomaticUpdateState = UpdateNew;
				state = false;
			}
		}

		else if (state && editionInfo.editionDate != L"")
		{
			if (IsNewerVersion(editionInfo.editionDate, editionDate)) AutomaticUpdateState = UpdateNew;
			else if (IsNewerVersion(editionDate, editionInfo.editionDate)) AutomaticUpdateState = UpdateNewer;
			else AutomaticUpdateState = UpdateLatest;
		}

		if (against && !mandatoryUpdate)
		{
			for (int i = 1; i <= 10; i++)
			{
				if (offSignal) break;
				if (AutomaticUpdateState == UpdateNotStarted || AutomaticUpdateState == UpdateObtainInformation) break;

				this_thread::sleep_for(chrono::seconds(1));
			}
		}
		else
		{
			against = mandatoryUpdate = false;
			for (int i = 1; i <= 1800; i++)
			{
				if (offSignal) break;
				if (AutomaticUpdateState == UpdateNotStarted || AutomaticUpdateState == UpdateObtainInformation) break;

				this_thread::sleep_for(chrono::seconds(1));
			}
			updateTimes = 0;
		}
	}

	for (; !offSignal;)
	{
		if (AutomaticUpdateState == UpdateNotStarted || AutomaticUpdateState == UpdateObtainInformation) goto updateStart;
		this_thread::sleep_for(chrono::seconds(1));
	}
}