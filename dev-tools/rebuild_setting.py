import io, os, re, sys, json, subprocess

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
print("开始:", len(t), "B,", t.count("\n"), "行")

def safe_sub(a, b, tag):
    global t
    n = t.count(a)
    if n == 0:
        print(f"  [skip] {tag}")
        return
    t = t.replace(a, b)
    print(f"  {tag}: {n}")

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

def del_block_by_child(child_begin_name):
    """删除 BeginChild(child_begin_name) 所在的完整卡片块"""
    global t
    lines = t.split("\n")
    idx = next((i for i, ln in enumerate(lines) if f'BeginChild("{child_begin_name}"' in ln), None)
    if idx is None:
        print(f"  [skip] {child_begin_name}")
        return
    # 向上找最近的与 BeginChild 同缩进的 {
    k = idx
    while k > 0 and not lines[k].rstrip().endswith("{"):
        k -= 1
    depth = 0; seen = False; end = None
    for j in range(k, len(lines)):
        depth += depth_delta(lines[j])
        if "{" in lines[j]: seen = True
        if seen and depth == 0: end = j; break
    if end is None: return
    del lines[k:end + 1]
    t = "\n".join(lines)
    print(f"  [del] {child_begin_name}")

# ============================================================
# PHASE 1: 品牌 + 链接 + 文本（不依赖 i18n）
# ============================================================
t = t.replace("Inkeys", "AnyThingDraw")
t = t.replace("inkeys3", "anythingdraw3")
safe_sub("1330313497", "413043448", "B站UID")
safe_sub("alan-crl@foxmail.com", "admin@yfyw.top", "邮箱")
safe_sub("https://www.inkeys.top", "https://draw.yfyw.top", "官网")
safe_sub("https://github.com/Alan-CRL/AnyThingDraw", "https://github.com/XiaoYangTech/AnyThingDraw", "GitHub")
safe_sub("亿方万能画笔(屏幕批注工具).lnk", "亿方万能画笔.lnk", "lnk")
safe_sub("PPT演示助手 3 轻量版", "PPT演示助手", "PPT名")
safe_sub("同类软件悬浮窗拦截助手 3 轻量版", "同类软件悬浮窗拦截助手", "DDB名")
# 工具栏文字
safe_sub('L"选择(清空)"', 'L"选择并清空"', "选择并清空")
safe_sub('L"画笔"', 'L"批注"', "画笔→批注")
safe_sub('L"选项"', 'L"设置"', "选项→设置")
safe_sub('L"定格"', 'L"冻屏"', "定格→冻屏")
safe_sub('L"穿透"', 'L"鼠标"', "穿透→鼠标")
# 控件设置
safe_sub('ImGui::TextUnformatted("控件位置");', 'ImGui::TextUnformatted("控件设置");', "控件设置")
# 版本
safe_sub('text += L"\\n软件发布版本 " + (editionDate.length() >= 8 ? editionDate.substr(0, 4) + L"年" + editionDate.substr(4, 2) + L"月" + editionDate.substr(6, 2) + L"日" : editionDate) + L"（" + editionChannel + L"）";',
         'text += L"\\n软件发布版本 1.0.0";', "版本1.0.0")
# SeekBar 隐藏
safe_sub("_SeekBar].Color.v, 250);", "_SeekBar].Color.v, 0);", "SeekBar隐藏")
# 快捷方式
safe_sub("亿方万能画笔(屏幕批注工具).lnk", "亿方万能画笔.lnk", "lnk2")
print("PHASE 1 完成")

# ============================================================
# PHASE 2: i18n 内联（从 HEAD zh-CN.jsonc 取映射+修改值）
# ============================================================
raw = subprocess.run(["git", "show", "HEAD:智绘教/src/i18n/zh-CN.jsonc"],
                     capture_output=True, timeout=30, check=True).stdout.decode("utf-8-sig")
jl = [ln for ln in raw.split("\n") if not ln.lstrip().startswith("//")]
data = json.loads("\n".join(jl))
flat = {}
def fl(o, pre):
    for k, v in o.items():
        pp = (pre + "/" + k) if pre else k
        if isinstance(v, dict): fl(v, pp)
        else: flat[pp] = v
fl(data, "")

# 中文修正
zh_fix = [
    ("CPU", "处理器"), ("100ms", "100毫秒"), ("500ms", "500毫秒"),
    ("1s)", "1秒)"), ("3s)", "3秒)"), ("5s)", "5秒)"), ("10s)", "10秒"), ("30s)", "30秒"),
    ("触控屏幕", "智慧黑板、触摸一体机或平板"),
    ("用户ID", "用户标识符"),
    ("选项界面 UI 缩放", "选项界面缩放"),
    ("(BETA)", "(公测版)"),
    ("BETA 阶段", "公测阶段"),
]
for old_v, new_v in zh_fix:
    for k in flat:
        if old_v in flat[k]:
            flat[k] = flat[k].replace(old_v, new_v)

# 覆盖值
flat["SettingsUI/PlugIn/PPTHelper/N"] = "PPT演示助手"
flat["SettingsUI/PlugIn/DesktopDrawpadBlocker/N"] = "同类软件悬浮窗拦截助手"

def cpp_esc(v):
    return v.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n")

miss = []
def rep_ia(m):
    kind, key = m.group(1), m.group(2)
    v = flat.get(key)
    if v is None:
        miss.append(key)
        return m.group(0)
    return ('L"' if kind == "IW" else '"') + cpp_esc(v) + '"'
t = re.sub(r'\b(IA|IW)\("([^"]+)"\)', rep_ia, t)
t = re.sub(r'(L?"(?:[^"\\]|\\.)*")\.c_str\(\)', r"\1", t)
for _ in range(8):
    t2 = re.sub(r'(L?"(?:[^"\\]|\\.)*")\s*\+\s*(L?"(?:[^"\\]|\\.)*")', r"\1\2", t)
    if t2 == t: break
    t = t2
print(f"PHASE 2 完成. IA/IW 残留: {t.count('IA(') + t.count('IW(')} 缺键: {miss[:3]}")

# ============================================================
# PHASE 3: I18n/Skin/Loading 系统清理
# ============================================================
t = t.replace('#include "IdtI18n.h"\n', "")

# I18n::identifying 行→只保留 zh-CN 分支内容
lines = t.split("\n")
i = 0
while i < len(lines):
    ln = lines[i]
    if "I18n::identifying" in ln and not ln.strip().startswith("//"):
        # 如果是 zh-CN 行→去掉 if 前缀保留内容
        if "zh-CN" in ln:
            indent = len(ln) - len(ln.lstrip())
            content = ln.lstrip()
            # 去掉 "if (...) " 前缀
            content = re.sub(r'if \(I18n::identifying == L"zh-CN"\)\s*', '', content)
            lines[i] = " " * indent + content
            # 删除后面的 else if 和 else 行
            j = i + 1
            while j < len(lines):
                if ("else if" in lines[j] or "else " in lines[j]) and ("I18n::identifying" in lines[j] or "idtLoadImage" in lines[j] or "ShellExecuteW" in lines[j] or "FindResource" in lines[j] or "hRes" in lines[j]):
                    j += 1
                    continue
                break
            del lines[i+1:j]
        else:
            # 非 zh-CN 的 identifying 行（可能是 zh-TW 或残留）
            # 检查是否是 else 行
            if "else" in ln:
                lines[i] = "// [i18n cleaned] " + ln.strip()[:40]
        i += 1
        continue
    i += 1
t = "\n".join(lines)

# I18n::load 行删除
lines = t.split("\n")
lines = [ln for ln in lines if "I18n::load(" not in ln]
t = "\n".join(lines)

# SkinMode==3 分支删除
lines = t.split("\n")
i = 0
while i < len(lines):
    if "else if (setlist.SkinMode == 3)" in lines[i]:
        depth = 0; seen = False; end = None
        for j in range(i, len(lines)):
            depth += depth_delta(lines[j])
            if "{" in lines[j]: seen = True
            if seen and depth == 0: end = j; break
        del lines[i:end + 1]
        continue
    i += 1
t = "\n".join(lines)
t = t.replace("if (setlist.SkinMode == 1 || setlist.SkinMode == 2)", "if (true)")
# 皮肤文件加载行
for a in [
    '\t\t\tidtLoadImage(&skin[1], L"PNG", L"skin1");\n',
    '\t\t\tidtLoadImage(&skin[3], L"PNG", L"skin1-3");\n',
]:
    t = t.replace(a, "")
# skin[3]/bskin3 残余行
lines = t.split("\n")
out = []
for ln in lines:
    if ("skin[3]" in ln or "bskin3" in ln) and "skin[2]" not in ln:
        continue
    out.append(ln)
t = "\n".join(out)

# showLoadingScreen 开关卡片
del_block_by_child("显示加载页面")
t = t.replace("bool PptComShowLoadingScreen = pptComSetlist.showLoadingScreen;\n", "")
lines = t.split("\n")
lines = [ln for ln in lines if "pptComSetlist.showLoadingScreen = PptComShowLoadingScreen" not in ln]
t = "\n".join(lines)
# FreezePPT 触发行
t = t.replace("\t\t\tif (!ppt_title_recond[ppt_title] && pptComSetlist.showLoadingScreen) FreezePPT = true;\n", "")

# SetSkinMode/SkinMode 引用
t = t.replace("setlist.SetSkinMode = 0;\n", "")
t = t.replace("setlist.SkinMode = 1;\n", "")
lines = t.split("\n")
lines = [ln for ln in lines if "int SetSkinMode" not in ln and "SetSkinMode == i" not in ln and "SetSkinMode == 0" not in ln]
t = "\n".join(lines)
# 主题 combo 块
del_block_by_child("##主题")
# selectLanguage 局部
lines = t.split("\n")
lines = [ln for ln in lines if "int SelectLanguage" not in ln and "SelectLanguage == i" not in ln and "SelectLanguage = i;" not in ln]
t = "\n".join(lines)
# 语言 combo 块
del_block_by_child("##语言")

print("PHASE 3 完成")

# ============================================================
# PHASE 4: 块删除
# ============================================================
del_block_by_child("配置保存#2")  # 历史画布保存
# 社区名片
t = re.sub(r'\t*// 社区名片\n(?:[^\n]*\n)*?\t*// 赞助我们', '\t// 赞助我们', t)
# 主页QQ号
safe_sub('ImGui::TextUnformatted("2685549821");', '', "QQ号")

# ============================================================
# PHASE 5: 新开关卡片
# ============================================================
# 橡皮开关卡片：在抬笔平滑笔迹 Toggle 所在卡片后
smooth = 'ImGui::Toggle("##抬笔平滑笔迹", &SmoothWriting, config);'
if smooth in t:
    # 找该 Toggle 所在的卡片块的 EndChild
    si = t.index(smooth)
    end_marker = "ImGui::EndChild();"
    ei = t.index(end_marker, si) + len(end_marker)
    # 找包裹 }
    while t[ei-1] != "}":
        ei = t.index("}", ei) + 1
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
    t = t[:ei] + new_card + t[ei:]
    print("  橡皮卡片 OK")
else:
    print("  [skip] 抬笔平滑笔迹 Toggle")

# 绘制#3 分组扩高
safe_sub('BeginChild("绘制#3", { 750.0f * settingGlobalScale,90.0f * settingGlobalScale }, false',
         'BeginChild("绘制#3", { 750.0f * settingGlobalScale,160.0f * settingGlobalScale }, false', "绘制#3扩高")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("全部完成:", len(t), "字节,", t.count("\n"), "行")
print("检查: IA/IW=", t.count("IA(") + t.count("IW("), " SkinMode=", t.count("SkinMode"), " I18n=", t.count("I18n::"), " 马年=", t.count("马年"))
