import io, os, re, sys, json, subprocess

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
print("初始:", len(t), "字节,", t.count("\n"), "行")

def depth_delta(line):
    d = 0; in_str = False; i = 0
    while i < len(line):
        c = line[i]
        if in_str:
            if c == "\\": i += 2; continue
            if c == '"': in_str = False
        else:
            if c == '"': in_str = True
            elif line[i:i+2] == "//": break
            elif c == "{": d += 1
            elif c == "}": d -= 1
        i += 1
    return d

def del_card(comment_or_anchor=None, match_in=None):
    tag = (comment_or_anchor or match_in or "?")[:30]
    """删除从包裹{到配平}的块。match_in 用于定位（如 BeginChild 名）。"""
    global t
    lines = t.split("\n")
    if match_in:
        idx = next((i for i, ln in enumerate(lines) if match_in in ln), None)
        if idx is None: print(f"  跳过 {tag}"); return
    else:
        idx = next((i for i, ln in enumerate(lines) if comment_or_anchor in ln), None)
        if idx is None: print(f"  跳过 {tag}"); return
    s = idx
    while s > 0 and lines[s].rstrip() not in ("\t\t\t\t\t{", "\t\t\t\t\t\t{", "\t\t\t\t{"):
        s -= 1
    depth = 0; seen = False; end = None
    for j in range(s, len(lines)):
        depth += depth_delta(lines[j])
        if "{" in lines[j]: seen = True
        if seen and depth == 0:
            end = j; break
    del lines[s:end + 1]
    t = "\n".join(lines)
    print(f"  删除 {tag} OK")

def sub_all(a, b, tag):
    global t
    n = t.count(a)
    if n == 0: print(f"  跳过 {tag}"); return
    t = t.replace(a, b)
    print(f"  {tag}: {n}处")

# ===== Phase 1: 品牌与文本 =====
print("Phase 1: 品牌与文本")
sub_all("Inkeys", "AnyThingDraw", "Inkeys→AnyThingDraw")
sub_all("inkeys3", "anythingdraw3", "inkeys3")
# 文本替换
sub_all("1330313497", "413043448", "B站UID")
sub_all("alan-crl@foxmail.com", "admin@yfyw.top", "邮箱")
sub_all("https://www.inkeys.top", "https://draw.yfyw.top", "官网")
sub_all("https://github.com/Alan-CRL/AnyThingDraw", "https://github.com/XiaoYangTech/AnyThingDraw", "GitHub")
sub_all("亿方万能画笔(屏幕批注工具).lnk", "亿方万能画笔.lnk", "快捷方式")
sub_all("PPT演示助手 3 轻量版", "PPT演示助手", "PPT名")
sub_all("同类软件悬浮窗拦截助手 3 轻量版", "同类软件悬浮窗拦截助手", "DDB名")
sub_all("L\"选择(清空)\"", "L\"选择并清空\"", "选择并清空")
sub_all("L\"画笔\"", "L\"批注\"", "批注")
sub_all("L\"选项\"", "L\"设置\"", "设置")
sub_all("L\"定格\"", "L\"冻屏\"", "冻屏")
sub_all("L\"穿透\"", "L\"鼠标\"", "鼠标")
# 版本显示
v_old = 'text += L"\\n软件发布版本 " + (editionDate.length() >= 8 ? editionDate.substr(0, 4) + L"年" + editionDate.substr(4, 2) + L"月" + editionDate.substr(6, 2) + L"日" : editionDate) + L"（" + editionChannel + L"）";'
v_new = 'text += L"\\n软件发布版本 1.0.0";'
sub_all(v_old, v_new, "版本1.0.0")
# SeekBar 隐藏
sub_all("_SeekBar].Color.v, 250);", "_SeekBar].Color.v, 0);", "SeekBar隐藏")
# DDB 文案
a = 'ImGui::TextWrapped("插件仅供学习交流和研究使用，不得用于其他任何用途。\\n同类软件悬浮窗拦截助手(DesktopDrawpadBlocker)是依据 GPLv3 许可协议发布的开源软件。\\n并在 Github 仓库得到发布：https://github.com/Alan-CRL/DesktopDrawpadBlocker\\n我们发布这款程序，希望它有用，但不承诺任何质量保证责任。\\n用户在使用该插件时，需自行承担由此产生的后果和影响，使用插件则视为同意此协议。");'
b = 'ImGui::TextWrapped("同类软件悬浮窗拦截助手(DesktopDrawpadBlocker)是依据 GPLv3 许可协议发布的开源软件。\\nGithub 仓库： https://github.com/Alan-CRL/DesktopDrawpadBlocker\\n如果因为使用本插件功能出现问题，可以反馈给插件原作者亦或是本项目（亿方万能画笔）的开发者。");'
sub_all(a, b, "DDB文案")
# 控件位置→控件设置
sub_all('ImGui::TextUnformatted("控件位置");', 'ImGui::TextUnformatted("控件设置");', "控件设置")
# 马年迎新选项删除
sub_all('vec.emplace_back(_strdup(("马年迎新")));', '', "马年迎新")
# CPU→处理器
sub_all("占用更多的CPU资源", "占用更多的处理器资源", "CPU")
sub_all("拥有强大 CPU 的设备", "拥有强大处理器的设备", "CPU2")

# ===== Phase 2: i18n 内联 =====
print("Phase 2: i18n 内联")
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
print(f"  键数: {len(flat)}")
# 中文修正（本土化改造）
zh_fix = [
    ("CPU", "处理器"),
    ("100ms", "100毫秒"), ("500ms", "500毫秒"), ("1s)", "1秒)"), ("3s)", "3秒)"),
    ("5s)", "5秒)"), ("10s)", "10秒"), ("30s)", "30秒"),
    ("触控屏幕", "智慧黑板、触摸一体机或平板"),
    ("用户ID", "用户标识符"),
    ("选项界面 UI 缩放", "选项界面缩放"),
    ("极限性能绘图(BETA)", "极限性能绘图(公测版)"),
    ("隐藏触控光标(BETA)", "隐藏触控光标(公测版)"),
    ("BETA 阶段", "公测阶段"),
    ("Microsoft PowerPoint 2007 和 Kingsoft WPS 2013", "微软办公套件 PowerPoint 2007 和金山WPS办公软件 2013"),
    (" 3 轻量版", " 3 轻量版"),
    ("QQ 用户群", "QQ 用户群"),
    ("亿方万能画笔", "亿方万能画笔"),
]
for old_v, new_v in zh_fix:
    for k in flat:
        if old_v in flat[k]:
            flat[k] = flat[k].replace(old_v, new_v)
# 特殊：版本标签去掉 LTS
if "SettingsUI/Version/Info/ReleaseVersion" in flat:
    pass  # 版本显示在代码里处理

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
t = re.sub(r'(L?"(?:[^"\\]|\\.)*")\.c_str\(\)', r"\1", t)
for _ in range(8):
    n1 = len(re.findall(r'(L?"(?:[^"\\]|\\.)*")\s*\+\s*(L?"(?:[^"\\]|\\.)*")', t))
    t = re.sub(r'(L?"(?:[^"\\]|\\.)*")\s*\+\s*(L?"(?:[^"\\]|\\.)*")', r"\1\2", t)
    if n1 == 0: break
print(f"  内联完成 残留: {t.count('IA(')+t.count('IW(')} 缺键: {miss[:3]}")

# ===== Phase 3: 块删除 =====
print("Phase 3: 块删除")
# 社区名片
del_card("// 社区名片", "// 赞助我们")
# 主页QQ号
del_card(None, 'TextUnformatted("2685549821")')
# 反馈按钮+二维码
del_card(None, 'BeginChild("显示加载页面"')
# 历史画布保存
del_card(None, "配置保存#2")
# 更新渠道（LimitUpdate 到 AnyThingDraw3Update）
si = next((i for i, ln in enumerate(t.split("\n")) if "LimitUpdate" in ln), None)
if si is not None:
    lines = t.split("\n")
    ei = next((i for i, ln in enumerate(lines) if "AnyThingDraw3Update" in ln or "Inkeys3Update" in ln), None)
    if ei and ei > si:
        del lines[si:ei]
        t = "\n".join(lines)
        print("  更新渠道块删除 OK")
# 主题选择器
del_card(None, 'vec.emplace_back(_strdup(("推荐皮肤")));')
# 首启语言检测
try:
    si = next(i for i, ln in enumerate(t.split("\n")) if "GetUserDefaultUILanguage" in ln)
    lines = t.split("\n")
    k = si
    while lines[k].rstrip() != "{":
        k -= 1
    depth = 0; seen = False; ei = None
    for j in range(k, len(lines)):
        depth += depth_delta(lines[j])
        if "{" in lines[j]: seen = True
        if seen and depth == 0: ei = j; break
    del lines[k:ei + 1]
    t = "\n".join(lines)
    print("  首启语言检测删除 OK")
except StopIteration:
    print("  跳过 首启语言检测")

# I18N 初始化块
try:
    si = next(i for i, ln in enumerate(t.split("\n")) if "I18N初始化" in ln)
    lines = t.split("\n")
    k = si
    while lines[k].rstrip() != "{":
        k -= 1
    depth = 0; seen = False; ei = None
    for j in range(k, len(lines)):
        depth += depth_delta(lines[j])
        if "{" in lines[j]: seen = True
        if seen and depth == 0: ei = j; break
    del lines[k:ei + 1]
    t = "\n".join(lines)
    print("  I18N初始化删除 OK")
except StopIteration:
    print("  跳过 I18N初始化")

# 点名器/ClassIsland 组件
try:
    si = next(i for i, ln in enumerate(t.split("\n")) if 'BeginChild("组件#4"' in ln)
    lines = t.split("\n")
    ei = next((i for i, ln in enumerate(lines) if "PPT演示助手-介绍" in ln and i > si + 300), None)
    if ei is None:
        ei = si + 500
    del lines[si:ei]
    t = "\n".join(lines)
    print("  点名器/ClassIsland 组件删除 OK")
except StopIteration:
    print("  跳过 点名器")

# 语言 tab
try:
    si = next(i for i, ln in enumerate(t.split("\n")) if "case settingTabEnum::Language:" in ln)
    lines = t.split("\n")
    depth = 0; seen = False; ei = None
    for j in range(si, len(lines)):
        depth += depth_delta(lines[j])
        if "{" in lines[j]: seen = True
        if seen and depth == 0: ei = j; break
    del lines[si:ei + 1]
    t = "\n".join(lines)
    # 导航按钮
    for i2, ln in enumerate(lines):
        if "settingTab = settingTabEnum::Language;" in ln:
            k = i2
            while lines[k].rstrip() != "{": k -= 1
            e = i2
            while lines[e].rstrip() != "}": e += 1
            del lines[k:e + 1]
            break
    t = "\n".join(lines)
    print("  语言tab删除 OK")
except StopIteration:
    print("  跳过 语言tab")

# ===== Phase 4: IdtI18n include 移除 =====
sub_all('#include "IdtI18n.h"\n', '', "IdtI18n include")

# ===== Phase 5: 新功能插入 =====
print("Phase 5: 新功能插入")
# 橡皮开关卡片：在 抬笔平滑笔迹 Toggle 后
smooth_toggle = 'ImGui::Toggle("##抬笔平滑笔迹", &SmoothWriting, config);'
if smooth_toggle in t:
    end_m = "ImGui::EndChild();\n\t\t\t\t\t}"
    end_idx = t.index(end_m, t.index(smooth_toggle)) + len(end_m)
    new_card = """

						{
							ImGui::SetCursorPosY(ImGui::GetCursorPosY() + 10.0f * settingGlobalScale);
							PushStyleVarNum++, ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0.0f, 0.0f));
							PushStyleVarNum++, ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, 4.0f);
							PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_ChildBg, IM_COL32(251, 251, 251, 255));
							ImGui::BeginChild("橡皮快捷清空", { 750.0f * settingGlobalScale,60.0f * settingGlobalScale }, true, ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);

							float cursosPosY = 0;
							{
								ImGui::SetCursorPos({ 20.0f * settingGlobalScale, cursosPosY + 22.0f * settingGlobalScale });
								ImFontMain->Scale = 0.6f, PushFontNum++, ImGui::PushFont(ImFontMain);
								PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0, 0, 0, 255));
								ImGui::TextUnformatted("双击或右键橡皮快速清空并切回批注");
							}
							{
								ImGui::SetCursorPos({ 690.0f * settingGlobalScale, cursosPosY + 20.0f * settingGlobalScale });
								PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_FrameBg, IM_COL32(0, 0, 0, 6));
								PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_FrameBgHovered, IM_COL32(0, 0, 0, 15));
								PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Button, IM_COL32(0, 95, 184, 255));
								PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_ButtonHovered, IM_COL32(0, 95, 184, 230));
								if (!EraserQuickClean)
								{
									PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0, 0, 0, 155));
									PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_BorderShadow, IM_COL32(0, 0, 0, 155));
								}
								else
								{
									PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(255, 255, 255, 255));
									PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_BorderShadow, IM_COL32(0, 95, 184, 255));
								}
								ImGui::Toggle("##双击或右键橡皮快速清空并切回批注", &EraserQuickClean, config);

								if (setlist.eraserQuickClean != EraserQuickClean)
								{
									setlist.eraserQuickClean = EraserQuickClean;
									WriteSetting();
								}
							}

							{
								if (PushStyleColorNum >= 0) ImGui::PopStyleColor(PushStyleColorNum), PushStyleColorNum = 0;
								if (PushStyleVarNum >= 0) ImGui::PopStyleVar(PushStyleVarNum), PushStyleVarNum = 0;
								while (PushFontNum) PushFontNum--, ImGui::PopFont();
							}
							ImGui::EndChild();
						}"""
    t = t[:end_idx] + new_card + t[end_idx:]
    print("  橡皮卡片插入 OK")
else:
    print("  跳过 橡皮卡片 (smooth toggle not found)")

# ===== 写入 =====
wr = io.open(p, "w", encoding="utf-8", newline="")
wr.write(t)
wr.close()
print("写入完成:", len(t), "字节,", t.count("\n"), "行")
