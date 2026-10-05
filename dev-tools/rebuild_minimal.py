import io, os, re, sys, json, subprocess

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
print("初始:", len(t), "字节")

# ===== 1. 品牌 =====
t = t.replace("Inkeys", "AnyThingDraw")
t = t.replace("inkeys3", "anythingdraw3")
t = t.replace('import Inkeys.Thread.Status', 'import AnyThingDraw.Thread.Status')

# ===== 2. 文本/链接 =====
t = t.replace("1330313497", "413043448")
t = t.replace("alan-crl@foxmail.com", "admin@yfyw.top")
t = t.replace("https://www.inkeys.top", "https://draw.yfyw.top")
t = t.replace("https://github.com/Alan-CRL/AnyThingDraw", "https://github.com/XiaoYangTech/AnyThingDraw")
t = t.replace("亿方万能画笔(屏幕批注工具).lnk", "亿方万能画笔.lnk")
t = t.replace("PPT演示助手 3 轻量版", "PPT演示助手")
t = t.replace("同类软件悬浮窗拦截助手 3 轻量版", "同类软件悬浮窗拦截助手")
t = t.replace('L"选择(清空)"', 'L"选择并清空"')
t = t.replace('L"画笔"', 'L"批注"')
t = t.replace('L"选项"', 'L"设置"')
t = t.replace('L"定格"', 'L"冻屏"')
t = t.replace('L"穿透"', 'L"鼠标"')
t = t.replace('ImGui::TextUnformatted("控件位置");', 'ImGui::TextUnformatted("控件设置");')

# ===== 3. i18n 内联（修改后的 zh-CN） =====
raw = subprocess.run(["git", "show", "HEAD:智绘教/src/i18n/zh-CN.jsonc"], capture_output=True, timeout=30, check=True).stdout.decode("utf-8-sig")
jl = [ln for ln in raw.split("\n") if not ln.lstrip().startswith("//")]
data = json.loads("\n".join(jl))
flat = {}
def flatten(o, pre):
    for k, v in o.items():
        pp = (pre + "/" + k) if pre else k
        if isinstance(v, dict): flatten(v, pp)
        else: flat[pp] = v
flatten(data, "")

# 中文修正
zh_pairs = [
    ("CPU", "处理器"), ("100ms", "100毫秒"), ("500ms", "500毫秒"),
    ("1s)", "1秒)"), ("3s)", "3秒)"), ("5s)", "5秒)"), ("10s)", "10秒"), ("30s)", "30秒"),
    ("触控屏幕", "智慧黑板、触摸一体机或平板"),
    ("用户ID", "用户标识符"),
    ("选项界面 UI 缩放", "选项界面缩放"),
    ("(BETA)", "(公测版)"),
    ("BETA 阶段", "公测阶段"),
    ("Microsoft PowerPoint 2007 和 Kingsoft WPS 2013", "微软办公套件 PowerPoint 2007 和金山WPS办公软件 2013"),
    ("支持 Microsoft PowerPoint 2007", "支持微软办公套件 PowerPoint 2007"),
]
for old_v, new_v in zh_pairs:
    for k in flat:
        if old_v in flat[k]:
            flat[k] = flat[k].replace(old_v, new_v)
# 特殊值覆盖
overrides = {
    "SettingsUI/Version/Info/ReleaseVersion": "1.0.0",
    "SettingsUI/PlugIn/PPTHelper/N": "PPT演示助手",
    "SettingsUI/PlugIn/DesktopDrawpadBlocker/N": "同类软件悬浮窗拦截助手",
}
for k, v in overrides.items():
    if k in flat:
        flat[k] = v

miss = []
def rep_ia(m):
    kind, key = m.group(1), m.group(2)
    v = flat.get(key)
    if v is None:
        miss.append(key)
        return m.group(0)
    ev = v.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n")
    return ('L"' if kind == "IW" else '"') + ev + '"'
t = re.sub(r'\b(IA|IW)\("([^"]+)"\)', rep_ia, t)
# .c_str() 清理
t = re.sub(r'(L?"(?:[^"\\]|\\.)*")\.c_str\(\)', r"\1", t)
# 字面量合并
for _ in range(8):
    t2 = re.sub(r'(L?"(?:[^"\\]|\\.)*")\s*\+\s*(L?"(?:[^"\\]|\\.)*")', r"\1\2", t)
    if t2 == t: break
    t = t2
# IdtI18n include 移除
t = t.replace('#include "IdtI18n.h"\n', "")

# ===== 4. 版本显示简化 =====
old_v = 'text += L"\\n软件发布版本 " + (editionDate.length() >= 8 ? editionDate.substr(0, 4) + L"年" + editionDate.substr(4, 2) + L"月" + editionDate.substr(6, 2) + L"日" : editionDate) + L"（" + editionChannel + L"）";'
if old_v in t:
    t = t.replace(old_v, 'text += L"\\n软件发布版本 " + editionDate;')

# ===== 检查 =====
res = t.count("IA(") + t.count("IW(")
print("IA/IW 残留:", res)
print("大小:", len(t), "字节,", t.count("\n"), "行")

wr = io.open(p, "w", encoding="utf-8", newline="")
wr.write(t)
wr.close()
print("写入完成")

print("=== i18n/skin cleanup ===")
exec(open("cleanup_i18n.py", encoding="utf-8").read())
