#include "ATDrawNet.h"
#include "jsoncpp/json.h"

#pragma comment(lib, "libssl_static.lib")
#pragma comment(lib, "libcrypto_static.lib")

#define CPPHTTPLIB_OPENSSL_SUPPORT
#include "cpphttplib/httplib.h"

std::string GetAppUpdateInformation(std::string os, std::string arch, std::string version)
{
	httplib::Result res;
	httplib::Headers headers =
	{
		{ "Cache-Control", "no-cache" },
		{ "Pragma", "no-cache" }
	};

	std::string query = "/apps/atdraw/api.php?route=app_update&os=" + os + "&arch=" + arch + "&version=" + version;

	{
		httplib::SSLClient scli("api.yfyw.top");
		scli.set_follow_location(true);
		scli.set_connection_timeout(5);
		scli.set_read_timeout(10);

		res = scli.Get(query.c_str(), headers);
		if (!res || res->status != 200)
		{
			httplib::Client cli("api.yfyw.top");
			cli.set_follow_location(true);
			cli.set_connection_timeout(5);
			cli.set_read_timeout(10);

			res = cli.Get(query.c_str(), headers);
		}

		if (res && res->status == 200)
		{
			std::string body = res->body;
			if (body.compare(0, 3, "\xEF\xBB\xBF") == 0) body = body.substr(3);
			return body;
		}
	}

	return "Error";
}

bool ReportDevicePing(std::string deviceKey, std::string deviceName)
{
	if (deviceKey.empty()) return false;

	httplib::SSLClient scli("api.yfyw.top");
	scli.set_follow_location(true);
	scli.set_connection_timeout(5);
	scli.set_read_timeout(10);

	Json::Value body;
	body["device_key"] = deviceKey;
	body["device_name"] = deviceName;
	body["os"] = "Windows";

	Json::StreamWriterBuilder builder;
	builder["indentation"] = "";
	std::string bodyStr = Json::writeString(builder, body);

	auto res = scli.Post("/apps/atdraw/api.php?route=client_ping", bodyStr, "application/json");
	return res && res->status == 200;
}
bool DownloadEdition(std::string domain, std::string path, std::wstring directory, std::wstring fileName, std::atomic_ullong& downloadedSize, std::string referer)
{
	httplib::Result res;
	httplib::Headers headers =
	{
		{ "Cache-Control", "no-cache" },
		{ "Pragma", "no-cache" },
		{ "Referer", referer.c_str() }
	};

	std::ofstream file;
	auto callback = [&](const char* data, size_t data_length)
		{
			file.write(data, data_length);
			downloadedSize += data_length;
			return true;
		};

	{
		file.open(directory + fileName, std::ios::binary | std::ios::out | std::ios::trunc);
		if (file)
		{
			file.seekp(0);

			// 使用 Https
			httplib::SSLClient scli(domain);
			scli.set_follow_location(true);
			scli.set_connection_timeout(5);
			res = scli.Get(path.c_str(), callback);
		}
		file.close();
	}
	if (!(res && res->status == 200))
	{
		file.open(directory + fileName, std::ios::binary | std::ios::out | std::ios::trunc);
		if (file)
		{
			file.seekp(0);

			// 使用 Http
			httplib::Client cli(domain);
			cli.set_follow_location(true);
			cli.set_connection_timeout(5);
			res = cli.Get(path.c_str(), callback);
		}
		file.close();
	}

	if (res && res->status == 200) return true;
	return false;
}