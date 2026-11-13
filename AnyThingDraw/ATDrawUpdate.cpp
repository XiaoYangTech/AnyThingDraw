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
		string architecture;
		bool enableAutoUpdate;
	};

	UpdateTargetSnapshot GetUpdateTargetSnapshot()
	{
		shared_lock<shared_mutex> lock(setlistUpdateMutex);
		return { setlist.updateArchitecture, setlist.enableAutoUpdate };
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

EditionInfoClass GetEditionInfo(string arch)
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
	if (_waccess((userDataPath + L"installer").c_str(), 4) == 0)
	{
		filesystem::remove_all(userDataPath + L"installer", ec);
		filesystem::create_directory(userDataPath + L"installer", ec);
	}
	else filesystem::create_directory(userDataPath + L"installer", ec);

	string prefix, domain, path;
	splitUrl(url, prefix, domain, path);

	state->downloadedSize.store(0);
	state->fileSize.store(editionInfo.fileSize.load());

	wstring timestamp = getTimestamp();
	bool reslut = DownloadEdition(domain, path, userDataPath + L"installer\\", L"new_procedure_" + timestamp + L".tmp", state->downloadedSize, GetRefererInfo());

	if (reslut)
	{
		error_code ec;
		filesystem::remove(userDataPath + L"installer\\new_procedure_" + timestamp + L".exe", ec);
		filesystem::remove(userDataPath + L"installer\\" + editionInfo.representation, ec);

		filesystem::rename(userDataPath + L"installer\\new_procedure_" + timestamp + L".tmp", userDataPath + L"installer\\new_procedure_" + timestamp + L".zip", ec);
		if (ec) return UpdateDownloadDamage;

		HZIP hz = OpenZip((userDataPath + L"installer\\new_procedure_" + timestamp + L".zip").c_str(), 0);
		SetUnzipBaseDir(hz, (userDataPath + L"installer").c_str());
		ZIPENTRY ze;
		GetZipItem(hz, -1, &ze);
		int numitems = ze.index;
		for (int i = 0; i < numitems; i++)
		{
			GetZipItem(hz, i, &ze);
			UnzipItem(hz, i, ze.name);
		}
		CloseZip(hz);

		filesystem::remove(userDataPath + L"installer\\new_procedure_" + timestamp + L".zip", ec);
		filesystem::rename(userDataPath + L"installer\\" + editionInfo.representation, userDataPath + L"installer\\new_procedure_" + timestamp + L".exe", ec);
		if (ec) return UpdateDownloadDamage;

		string hash_md5, hash_sha256;
		{
			hashwrapper* myWrapper = new md5wrapper();
			hash_md5 = myWrapper->getHashFromFileW(userDataPath + L"installer\\new_procedure_" + timestamp + L".exe");
			delete myWrapper;
		}
		{
			hashwrapper* myWrapper = new sha256wrapper();
			hash_sha256 = myWrapper->getHashFromFileW(userDataPath + L"installer\\new_procedure_" + timestamp + L".exe");
			delete myWrapper;
		}

		//创建 update.json 文件，指示更新
		if (editionInfo.hash_md5 == hash_md5 && editionInfo.hash_sha256 == hash_sha256)
		{
			if (!GetUpdateTargetSnapshot().enableAutoUpdate && !mandatoryUpdate)
			{
				error_code ec;
				filesystem::remove(userDataPath + L"installer\\new_procedure_" + timestamp + L".exe", ec);

				return UpdateNew;
			}
			else
			{
				Json::Value root;

				root["edition"] = Json::Value(utf16ToUtf8(editionInfo.editionDate));
				root["path"] = Json::Value("installer\\new_procedure_" + utf16ToUtf8(timestamp) + ".exe");
				root["representation"] = Json::Value("new_procedure_" + utf16ToUtf8(timestamp) + ".exe");

				root["hash"]["md5"] = Json::Value(editionInfo.hash_md5);
				root["hash"]["sha256"] = Json::Value(editionInfo.hash_sha256);

				root["arch"] = Json::Value(arch);

				root["old_name"] = Json::Value(utf16ToUtf8(GetCurrentExeName()));
				if (mandatoryUpdate) root["MandatoryUpdate"] = Json::Value(mandatoryUpdate);

				Json::StreamWriterBuilder outjson;
				outjson.settings_["emitUTF8"] = true;
				unique_ptr<Json::StreamWriter> writer(outjson.newStreamWriter());
				ofstream writejson(userDataPath + L"installer\\update.json", ios::binary);
				writejson << "\xEF\xBB\xBF";
				writer->write(root, &writejson);
				writejson.close();
			}
		}
		else
		{
			error_code ec;
			filesystem::remove(userDataPath + L"installer\\new_procedure_" + timestamp + L".exe", ec);

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
	if (_waccess((userDataPath + L"installer").c_str(), 4) == 0)
	{
		filesystem::remove_all(userDataPath + L"installer", ec);
		filesystem::create_directory(userDataPath + L"installer", ec);
	}
	else filesystem::create_directory(userDataPath + L"installer", ec);

	string prefix, domain, path;
	splitUrl(url, prefix, domain, path);
	if (domain.empty()) return UpdateDownloadFail;

	state->downloadedSize.store(0);
	state->fileSize.store(editionInfo.fileSize.load());

	wstring timestamp = getTimestamp();
	wstring tmpFile = L"atdraw_setup_" + timestamp + L".tmp";
	wstring exeFile = L"atdraw_setup_" + timestamp + L".exe";

	if (!DownloadEdition(domain, path, userDataPath + L"installer\\", tmpFile, state->downloadedSize, GetRefererInfo()))
		return UpdateDownloadFail;

	filesystem::remove(userDataPath + L"installer\\" + exeFile, ec);
	filesystem::rename(userDataPath + L"installer\\" + tmpFile, userDataPath + L"installer\\" + exeFile, ec);
	if (ec) return UpdateDownloadDamage;

	// 云端提供了校验值 / 大小时校验安装包
	if (!editionInfo.hash_sha256.empty())
	{
		hashwrapper* myWrapper = new sha256wrapper();
		string hash_sha256 = myWrapper->getHashFromFileW(userDataPath + L"installer\\" + exeFile);
		delete myWrapper;
		if (hash_sha256 != editionInfo.hash_sha256)
		{
			filesystem::remove(userDataPath + L"installer\\" + exeFile, ec);
			return UpdateDownloadDamage;
		}
	}
	if (editionInfo.fileSize.load() > 0 && state->downloadedSize.load() != editionInfo.fileSize.load())
	{
		filesystem::remove(userDataPath + L"installer\\" + exeFile, ec);
		return UpdateDownloadDamage;
	}

	// 下载完成后不立即安装：写入待更新标记，下次启动软件时自动完成更新
	// （避免使用期间被打断，安装动作推迟到下一次打开软件）
	{
		Json::Value root;
		root["version"] = Json::Value(utf16ToUtf8(editionInfo.editionDate));
		root["installer"] = Json::Value("installer\\" + utf16ToUtf8(exeFile));

		Json::StreamWriterBuilder outjson;
		outjson.settings_["emitUTF8"] = true;
		unique_ptr<Json::StreamWriter> writer(outjson.newStreamWriter());
		ofstream writejson(userDataPath + L"installer\\pending_update.json", ios::binary);
		writejson << "\xEF\xBB\xBF";
		writer->write(root, &writejson);
		writejson.close();
	}

	AutomaticUpdateState = UpdateRestart;

	return UpdateRestart;
}

// 待更新标记是否就绪（已下载同一版本的安装包，等待下次启动安装）
static bool IsPendingUpdateReady(const wstring& version)
{
	wstring pendingPath = userDataPath + L"installer\\pending_update.json";
	if (_waccess(pendingPath.c_str(), 4) != 0) return false;

	ifstream readjson(pendingPath, ios::binary);
	if (!readjson) return false;
	string content((istreambuf_iterator<char>(readjson)), istreambuf_iterator<char>());
	readjson.close();
	if (content.compare(0, 3, "\xEF\xBB\xBF") == 0) content = content.substr(3);

	Json::Reader reader;
	Json::Value root;
	if (!reader.parse(content, root)) return false;
	if (!root.isMember("version") || !root["version"].isString()) return false;
	if (utf8ToUtf16(root["version"].asString()) != version) return false;
	if (!root.isMember("installer") || !root["installer"].isString()) return false;

	wstring installerPath = userDataPath + utf8ToUtf16(root["installer"].asString());
	return _waccess(installerPath.c_str(), 4) == 0;
}

// ===== 更新失败冷却：同版本安装失败多次后暂停自动更新，避免无限重下/重装 =====
static wstring GetUpdateStatePath()
{
	return userDataPath + L"installer\\update_state.json";
}

static bool LoadUpdateState(wstring& version, int& attempts, long long& lastAttempt)
{
	version.clear(); attempts = 0; lastAttempt = 0;
	ifstream file(GetUpdateStatePath(), ios::binary);
	if (!file) return false;
	string content((istreambuf_iterator<char>(file)), istreambuf_iterator<char>());
	if (content.size() >= 3 && static_cast<unsigned char>(content[0]) == 0xEF) content = content.substr(3);
	Json::Reader reader; Json::Value root;
	if (!reader.parse(content, root)) return false;
	if (root.isMember("version") && root["version"].isString()) version = utf8ToUtf16(root["version"].asString());
	if (root.isMember("attempts") && root["attempts"].isInt()) attempts = root["attempts"].asInt();
	if (root.isMember("last_attempt") && root["last_attempt"].isInt64()) lastAttempt = root["last_attempt"].asInt64();
	return true;
}

static void SaveUpdateState(const wstring& version, int attempts, long long lastAttempt)
{
	error_code ec;
	filesystem::create_directories(userDataPath + L"installer", ec);
	Json::Value root;
	root["version"] = Json::Value(utf16ToUtf8(version));
	root["attempts"] = Json::Value(attempts);
	root["last_attempt"] = Json::Value(static_cast<Json::Int64>(lastAttempt));
	Json::StreamWriterBuilder builder;
	builder.settings_["emitUTF8"] = true;
	unique_ptr<Json::StreamWriter> writer(builder.newStreamWriter());
	ofstream out(GetUpdateStatePath(), ios::binary);
	out << "\xEF\xBB\xBF";
	writer->write(root, &out);
}

static long long GetNowSeconds()
{
	return chrono::duration_cast<chrono::seconds>(chrono::system_clock::now().time_since_epoch()).count();
}

static bool IsUpdateCoolingDown(const wstring& version)
{
	wstring savedVersion; int attempts = 0; long long lastAttempt = 0;
	if (!LoadUpdateState(savedVersion, attempts, lastAttempt)) return false;
	if (savedVersion != version) return false;
	if (attempts < 2) return false;
	return (GetNowSeconds() - lastAttempt) < 6 * 60 * 60;
}

static void RecordUpdateAttempt(const wstring& version)
{
	wstring savedVersion; int attempts = 0; long long lastAttempt = 0;
	LoadUpdateState(savedVersion, attempts, lastAttempt);
	if (savedVersion != version) attempts = 0;
	SaveUpdateState(version, attempts + 1, GetNowSeconds());
}

// 启动时应用已下载的更新：静默运行安装程序（由安装程序结束本程序并启动新版本）。
// 关键：安装前必须先移除"待更新"标记——安装程序会 taskkill 本进程，
// 若等安装完再删标记，进程已被结束，标记残留会导致每次启动都再次安装（无限更新循环）。
void ApplyPendingUpdate()
{
	wstring pendingPath = userDataPath + L"installer\\pending_update.json";
	wstring applyingPath = userDataPath + L"installer\\pending_update.applying";
	wstring updateJsonPath = userDataPath + L"installer\\update.json";
	error_code ec;

	// 上次安装中断留下的临时标记：直接清理
	filesystem::remove(applyingPath, ec);

	if (_waccess(pendingPath.c_str(), 4) != 0) return;

	string content;
	{
		ifstream readjson(pendingPath, ios::binary);
		if (!readjson)
		{
			filesystem::remove(pendingPath, ec);
			return;
		}
		content.assign((istreambuf_iterator<char>(readjson)), istreambuf_iterator<char>());
	}
	if (content.compare(0, 3, "\xEF\xBB\xBF") == 0) content = content.substr(3);

	Json::Reader reader;
	Json::Value root;
	if (!reader.parse(content, root) || !root.isMember("installer") || !root["installer"].isString())
	{
		filesystem::remove(pendingPath, ec);
		return;
	}

	// 版本校验：待安装版本必须比当前版本新，否则清除标记，避免反复安装同一版本
	wstring pendingVersion;
	if (root.isMember("version") && root["version"].isString()) pendingVersion = utf8ToUtf16(root["version"].asString());
	if (!pendingVersion.empty() && !IsNewerVersion(pendingVersion, editionDate))
	{
		ATDrawLogger->warn("[主线程][ATDrawUpdate] 待更新版本不高于当前版本，清除待更新标记");
		if (root.isMember("installer") && root["installer"].isString())
		{
			filesystem::remove(userDataPath + utf8ToUtf16(root["installer"].asString()), ec);
		}
		filesystem::remove(pendingPath, ec);
		filesystem::remove(updateJsonPath, ec);
		return;
	}

	wstring installerPath = userDataPath + utf8ToUtf16(root["installer"].asString());
	if (_waccess(installerPath.c_str(), 4) != 0)
	{
		filesystem::remove(pendingPath, ec);
		filesystem::remove(updateJsonPath, ec);
		return;
	}

	wstring installDir = globalPath;
	while (!installDir.empty() && installDir.back() == L'\\') installDir.pop_back();
	// 同版本多次安装失败：进入冷却，清理标记并跳过（防止跨启动的无限更新）
	if (!pendingVersion.empty() && IsUpdateCoolingDown(pendingVersion))
	{
		ATDrawLogger->warn("[主线程][ATDrawUpdate] 同版本更新多次失败，进入冷却，跳过本次自动安装");
		filesystem::remove(installerPath, ec);
		filesystem::remove(pendingPath, ec);
		filesystem::remove(applyingPath, ec);
		filesystem::remove(updateJsonPath, ec);
		return;
	}

	// 便携副本/改名副本：运行目录必须与注册表安装目录一致，否则不做静默安装
	{
		wchar_t regDirBuffer[MAX_PATH] = { 0 };
		DWORD regSize = sizeof(regDirBuffer);
		HKEY regKey = NULL;
		if (RegOpenKeyExW(HKEY_LOCAL_MACHINE, L"Software\\AnyThingDraw", 0, KEY_READ, &regKey) == ERROR_SUCCESS)
		{
			RegQueryValueExW(regKey, L"InstallDir", NULL, NULL, reinterpret_cast<LPBYTE>(regDirBuffer), &regSize);
			RegCloseKey(regKey);
		}
		wstring regDir = regDirBuffer;
		wstring runDir = globalPath;
		while (!regDir.empty() && (regDir.back() == L'\\' || regDir.back() == L'\/')) regDir.pop_back();
		while (!runDir.empty() && (runDir.back() == L'\\' || runDir.back() == L'\/')) runDir.pop_back();
		if (!regDir.empty() && _wcsicmp(regDir.c_str(), runDir.c_str()) != 0)
		{
			ATDrawLogger->warn("[主线程][ATDrawUpdate] 运行目录与安装目录不一致（便携/副本），跳过静默更新");
			filesystem::remove(installerPath, ec);
			filesystem::remove(pendingPath, ec);
			filesystem::remove(updateJsonPath, ec);
			return;
		}
	}

	wstring parameters = L"/S /D=" + installDir;

	ATDrawLogger->info("[主线程][ATDrawUpdate] 发现已下载的新版本，启动安装程序");
	ATDrawLogger->flush();

	// 启动安装程序前先移走待更新标记（安装程序会结束本进程，之后无法再清理）
	{
		filesystem::rename(pendingPath, applyingPath, ec);
		if (ec)
		{
			filesystem::remove(pendingPath, ec);
		}
		filesystem::remove(updateJsonPath, ec);
	}

	if (!pendingVersion.empty()) RecordUpdateAttempt(pendingVersion);

	SHELLEXECUTEINFOW sei = { 0 };
	sei.cbSize = sizeof(sei);
	sei.fMask = SEE_MASK_NOCLOSEPROCESS;
	sei.lpVerb = L"open";
	sei.lpFile = installerPath.c_str();
	sei.lpParameters = parameters.c_str();
	sei.nShow = SW_SHOWNORMAL;
	if (!ShellExecuteExW(&sei))
	{
		// UAC 被拒绝或安装程序无法启动：清理安装包，本次不更新（避免反复触发）
		ATDrawLogger->warn("[主线程][ATDrawUpdate] 安装程序启动失败或被取消，清理更新包");
		filesystem::remove(installerPath, ec);
		filesystem::remove(applyingPath, ec);
		return;
	}

	WaitForSingleObject(sei.hProcess, 300000);
	DWORD exitCode = 1;
	if (sei.hProcess)
	{
		GetExitCodeProcess(sei.hProcess, &exitCode);
		CloseHandle(sei.hProcess);
	}

	// 若本进程还活着，说明安装未完成（可能被拒绝/失败）：清理安装包与标记，避免下次重试同一包
	ATDrawLogger->warn("[主线程][ATDrawUpdate] 安装程序返回，退出码 " + to_string(exitCode));
	filesystem::remove(installerPath, ec);
	filesystem::remove(applyingPath, ec);
	filesystem::remove(pendingPath, ec);
	filesystem::remove(updateJsonPath, ec);
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
			editionInfo = GetEditionInfo(updateArch);

			if (editionInfo.errorCode != 200)
			{
				state = false, against = true;
				if (editionInfo.errorCode == 1) AutomaticUpdateState = UpdateInformationFail;
				else if (editionInfo.errorCode == 2) AutomaticUpdateState = UpdateInformationDamage;
				else AutomaticUpdateState = UpdateInformationUnStandardized;
			}
		}

		//下载最新版本
		if (state && editionInfo.editionDate != L"" && ((IsNewerVersion(editionInfo.editionDate, editionDate) && GetUpdateTargetSnapshot().enableAutoUpdate) || mandatoryUpdate))
		{
			if (editionInfo.path_size > 0 && !editionInfo.path[0].empty())
			{
				if (IsPendingUpdateReady(editionInfo.editionDate))
				{
					// 该版本的更新包已下载：等下次启动软件时自动安装
					AutomaticUpdateState = UpdateRestart;
					state = false;
				}
				else
				{
					// 亿方智云按架构返回了 NSIS 安装包：下载并记录为待更新
					AutomaticUpdateState = DownloadNewInstaller(&downloadNewProgramState, editionInfo, editionInfo.path[0], updateArch);
					state = false;
				}
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