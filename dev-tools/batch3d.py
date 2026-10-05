import io, os, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

def rd(p):
    return io.open(p, encoding="utf-8", newline="").read().replace("\r\n", "\n")

def wr(p, t):
    io.open(p, "w", encoding="utf-8", newline="").write(t)

# ===== 1. IdtConfiguration.cpp：ReadSetting 里加 DeviceKey 读取 =====
t = rd("IdtConfiguration.cpp")
if 'isMember("DeviceKey")' not in t:
    a = """\t\tif (setlistVal.isMember("StartUp") && setlistVal["StartUp"].isBool())
\t\t\tsetlist.startUp = setlistVal["StartUp"].asBool();"""
    assert a in t, "ReadSetting StartUp anchor"
    t = t.replace(a, a + """

\t\tif (setlistVal.isMember("BasicInfo") && setlistVal["BasicInfo"].isObject())
\t\t{
\t\t\tif (setlistVal["BasicInfo"].isMember("DeviceKey") && setlistVal["BasicInfo"]["DeviceKey"].isString())
\t\t\t\tdeviceKey = utf8ToUtf16(setlistVal["BasicInfo"]["DeviceKey"].asString());
\t\t}""")
    wr("IdtConfiguration.cpp", t)
    print("1. DeviceKey 读取 OK")

# ===== 2. IdtMain.cpp：生成块移到 ReadSetting 之后 =====
t = rd("IdtMain.cpp")
gen = """
\t\tif (deviceKey.empty())
\t\t{
\t\t\tstd::random_device rd;
\t\t\tstd::mt19937_64 gen(rd());
\t\t\tstd::uniform_int_distribution<int> dist(0, 15);
\t\t\tconst wchar_t* hexChars = L"0123456789abcdef";
\t\t\twstring key = L"le_";
\t\t\tfor (int i = 0; i < 32; i++) key += hexChars[dist(gen)];
\t\t\tdeviceKey = key;
\t\t\tWriteSetting();
\t\t}"""
assert gen in t, "gen block not found"
# 从原位置删除
t = t.replace(gen, "", 1)
# 插到 ReadSetting 之后
a = """\t\t\telse ReadSetting();
\t\t\tWriteSetting();
\t\t}"""
assert a in t
t = t.replace(a, a + "\n\n\t\t// 设备标识（亿方智云上报用，首次生成后持久化）\n\t\t{" + gen + "\n\t\t}", 1)
wr("IdtMain.cpp", t)
print("2. 生成时序调整 OK")
