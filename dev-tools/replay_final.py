# 图标替换由 C 阶段后统一处理
import io, os, re, sys, json, subprocess

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
print("开始:", t.count("\n"), "行")

def dd(ln):
    d = 0; ins = False; i = 0
    while i < len(ln):
        c = ln[i]
        if ins:
            if c == "\\": i += 2; continue
            if c == '"': ins = False
        else:
            if c == '"': ins = True
            elif ln[i:i+2] == "//": break
            elif c == "{": d += 1
            elif c == "}": d -= 1
        i += 1
    return d

def find_line(substr, start=0):
    ls = t.split("\n")
    for i in range(start, len(ls)):
        if substr in ls[i]:
            return i
    return -1

def block_range(line_idx):
    """从 line_idx（或其上方最近 '{' 结尾行）到配平结束行，返回 [s, e] 行号"""
    ls = t.split("\n")
    s = line_idx
    while s > 0 and not ls[s].rstrip().endswith("{"):
        s -= 1
    depth = 0; seen = False
    for j in range(s, len(ls)):
        depth += dd(ls[j])
        if "{" in ls[j]: seen = True
        if seen and depth == 0:
            return s, j
    raise RuntimeError("block unbalanced at %d" % line_idx)

def del_block(line_idx, verify=None):
    global t
    s, e = block_range(line_idx)
    if verify:
        seg = "\n".join(t.split("\n")[s:e+1])
        assert verify in seg, f"verify failed @{s+1}"
    ls = t.split("\n")
    del ls[s:e+1]
    t = "\n".join(ls)
    print(f"  [del {s+1}-{e+1}] ({e-s+1}行)")

def keep_zhcn(idx, strip_prefix):
    """把 idx 行去掉 if 前缀保留内容，删除后续 else 行（内容验证）"""
    global t
    ls = t.split("\n")
    ln = ls[idx]
    assert "I18n::identifying" in ln
    indent = ln[:len(ln) - len(ln.lstrip())]
    content = ln.strip()
    for pref in strip_prefix:
        content = content.replace(pref, "")
    ls[idx] = indent + content
    # 删除后续 else 行
    j = idx + 1
    removed = 0
    while j < len(ls) and removed < 3:
        s = ls[j].strip()
        if s.startswith("else ") or s.startswith("else if "):
            del ls[j]
            removed += 1
            continue
        break
    assert removed >= 1, f"no else removed @{idx+1}"
    t = "\n".join(ls)

# ============ A. 品牌 ============
t = t.replace("Inkeys", "AnyThingDraw")
t = t.replace("inkeys3", "anythingdraw3")
print("A. 品牌完成")

# ============ B. 简单替换 ============
def ss(a, b, tag):
    global t
    n = t.count(a)
    if n: t = t.replace(a, b); print(f"  {tag}: {n}")
    else: print(f"  [skip] {tag}")

ss("1330313497", "413043448", "B站UID")
ss("alan-crl@foxmail.com", "admin@yfyw.top", "邮箱")
ss("https://www.inkeys.top", "https://draw.yfyw.top", "官网")
ss("https://github.com/Alan-CRL/AnyThingDraw", "https://github.com/XiaoYangTech/AnyThingDraw", "GitHub")
ss("亿方万能画笔(屏幕批注工具)", "亿方万能画笔", "lnk名")
ss('L"选择(清空)"', 'L"选择并清空"', "选择并清空")
ss('ImGui::TextUnformatted("控件位置");', 'ImGui::TextUnformatted("控件设置");', "控件设置")
ss('_SeekBar].Color.v, 250);', '_SeekBar].Color.v, 0);', "SeekBar隐藏")
ss('text += L"\\n软件发布版本 " + (editionDate.length() >= 8 ? editionDate.substr(0, 4) + L"年" + editionDate.substr(4, 2) + L"月" + editionDate.substr(6, 2) + L"日" : editionDate) + L"（" + editionChannel + L"）";',
   'text += L"\\n软件发布版本 1.0.0";', "版本1.0.0")
print("B. 简单替换完成")

# ============ C. i18n 内联 ============
raw = subprocess.run(["git", "show", "0d9751b9:智绘教/src/i18n/zh-CN.jsonc"],
                     capture_output=True, timeout=30, check=True).stdout.decode("utf-8-sig")
data = json.loads("\n".join(ln for ln in raw.split("\n") if not ln.lstrip().startswith("//")))
flat = {}
def fl(o, pre):
    for k, v in o.items():
        pp = (pre + "/" + k) if pre else k
        if isinstance(v, dict): fl(v, pp)
        else: flat[pp] = v
fl(data, "")
for ov, nv in [("CPU", "处理器"), ("100ms", "100毫秒"), ("500ms", "500毫秒"),
               ("1s)", "1秒)"), ("3s)", "3秒)"), ("5s)", "5秒)"), ("10s)", "10秒"), ("30s)", "30秒"),
               ("触控屏幕", "智慧黑板、触摸一体机或平板"), ("用户ID", "用户标识符"),
               ("选项界面 UI 缩放", "选项界面缩放"), ("(BETA)", "(公测版)"), ("BETA 阶段", "公测阶段")]:
    for k in flat:
        if ov in flat[k]: flat[k] = flat[k].replace(ov, nv)
flat["SettingsUI/PlugIn/PPTHelper/N"] = "PPT演示助手"
flat["SettingsUI/PlugIn/DesktopDrawpadBlocker/N"] = "同类软件悬浮窗拦截助手"

miss = []
def rp(m):
    kind, key = m.group(1), m.group(2)
    v = flat.get(key)
    if v is None:
        miss.append(key); return m.group(0)
    ev = v.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n")
    return ('L"' if kind == "IW" else '"') + ev + '"'
t = re.sub(r'\b(IA|IW)\("([^"]+)"\)', rp, t)
t = re.sub(r'(L?"(?:[^"\\]|\\.)*")\.c_str\(\)', r"\1", t)
for _ in range(8):
    t2 = re.sub(r'(L?"(?:[^"\\]|\\.)*")\s*\+\s*(L?"(?:[^"\\]|\\.)*")', r"\1\2", t)
    if t2 == t: break
    t = t2
t = t.replace('#include "IdtI18n.h"\n', "")
print(f"C. i18n 内联完成 残留={t.count('IA(') + t.count('IW(')} 缺键={miss}")

# ============ D. 行锚定分支修复 ============
# D1. Home1/Home2
for img in ["Home1_zh-CN", "Home2_zh-CN"]:
    i = find_line(f'idtLoadImage(&SettingSign, L"PNG", L"{img}"')
    assert i >= 0, img
    keep_zhcn(i, ['if (I18n::identifying == L"zh-CN") '])
print("D1. Home图片完成")

# D2. 官网按钮
i = find_line('if (I18n::identifying == L"zh-CN") ShellExecuteW(0, 0, L"https://draw.yfyw.top"')
if i < 0:
    i = find_line('I18n::identifying == L"zh-CN") ShellExecuteW')
assert i >= 0, "官网"
keep_zhcn(i, ['if (I18n::identifying == L"zh-CN") '])
print("D2. 官网按钮完成")

# D3. QQ群：TextLink("6187208021") → 纯文本 1125655343
i = find_line('ImGui::TextLink("6187208021")')
if i >= 0:
    ls = t.split("\n")
    ln = ls[i]
    indent = ln[:len(ln) - len(ln.lstrip())]
    ls[i] = indent + 'ImGui::TextUnformatted("1125655343");'
    # 删除后续 { ShellExecuteW ... } 直到闭括号行
    j = i + 1
    assert ls[j].strip() == "{", ls[j]
    depth = 0
    end = None
    for k2 in range(j, len(ls)):
        depth += dd(ls[k2])
        if depth == 0:
            end = k2; break
    del ls[j:end+1]
    t = "\n".join(ls)
    print("D3. QQ群纯文本完成")
else:
    print("D3. [skip] QQ群")

# D4. 字体 if/else
i = find_line('if (I18n::identifying == L"zh-TW") hRes = FindResource(NULL, MAKEINTRESOURCE(258), L"TTF");')
assert i >= 0, "字体if"
ls = t.split("\n")
indent = ls[i][:len(ls[i]) - len(ls[i].lstrip())]
assert "MAKEINTRESOURCE(198)" in ls[i+1]
ls[i] = indent + 'hRes = FindResource(NULL, MAKEINTRESOURCE(198), L"TTF");'
del ls[i+1]
t = "\n".join(ls)
print("D4a. 字体if完成")

# D5. zh-TW 补字块删除
i = find_line("补充简化字")
if i >= 0:
    del_block(i - 1)  # i-1 是注释行，块从其上的 if 行开始——block_range 会回溯到 if 行的 {
    print("D5. zh-TW补字块完成")

# D6. AnyThingDraw3Update IA 键
ss('IA("SettingsUI/Version/AnyThingDraw3Update/N")', '"AnyThingDraw3 已经正式发布！"', "3Update N")
ss('IA("SettingsUI/Version/AnyThingDraw3Update/Download")', '"立即更新"', "3Update D")

# ============ E. 块删除 ============
# E1. 社区名片导航按钮（锚：5缩进注释+490坐标）
i = find_line("SetCursorPos({ 10.0f * settingGlobalScale,490.0f")
if i >= 0:
    ls = t.split("\n")
    s = i
    while s > 0 and "// 社区名片" not in ls[s]:
        s -= 1
    assert s >= 0 and i - s < 3, "社区名片锚"
    del_block(s)
    print("E1. 社区名片完成")
else:
    print("E1. [skip]")

# E2. 语言导航按钮（锚：f2b7 图标）
i = find_line("\\uf2b7")
if i >= 0:
    ls = t.split("\n")
    s = i
    while s > 0 and ls[s].rstrip() != "\t\t\t\t\t{":
        s -= 1
    assert "语言" in ls[s+1] or "语言" in ls[i], "语言按钮锚"
    del_block(s)
    print("E2. 语言按钮完成")
else:
    print("E2. [skip]")

# E3. 语言 case 块
i = find_line("case settingTabEnum::Language:")
if i >= 0:
    ls = t.split("\n")
    depth = 0; seen = False; end = None
    for j in range(i, len(ls)):
        depth += dd(ls[j])
        if "{" in ls[j]: seen = True
        if seen and depth == 0: end = j; break
    del ls[i:end+1]
    t = "\n".join(ls)
    print(f"E3. 语言case块删除 {i+1}-{end+1}")

# E4. 显示加载页面卡片
i = find_line('BeginChild("显示加载页面"')
if i >= 0:
    del_block(i, verify="显示加载页面")
    print("E4. 加载页面卡片完成")

# E5. 配置保存#2（历史画布）
i = find_line('BeginChild("配置保存#2"')
if i >= 0:
    del_block(i)
    print("E5. 历史画布卡片完成")

# E6. 反馈按钮+二维码
i = find_line('ImGui::TextLink("问题/建议反馈")')
if i >= 0:
    ls = t.split("\n")
    s = i
    while s > 0 and not ls[s].rstrip().endswith("{"):
        s -= 1
    # 该块的父级——回溯两级到块起点（TextLink 外还有一层 icon 块包裹）
    del_block(i)  # 先删 TextLink 所在包裹（含 tooltip）
    print("E6. 反馈块完成")

# E7. 主页QQ号→原项目GitHub仓库链接
i = find_line('ImGui::TextUnformatted("2685549821");')
if i >= 0:
    ls = t.split("\n")
    indent = ls[i][:len(ls[i]) - len(ls[i].lstrip())]
    ls[i] = indent + 'if (ImGui::TextLink("原项目GitHub仓库"))'
    ls.insert(i + 1, indent + '{')
    ls.insert(i + 2, indent + '\tShellExecuteW(0, 0, L"https://github.com/Alan-CRL/Inkeys", 0, 0, SW_SHOW);')
    ls.insert(i + 3, indent + '}')
    t = "\n".join(ls)
    print("E7. QQ号块改为原项目链接")

# E8. 主题 combo（含 vec 行）
i = find_line('BeginCombo("##主题"')
if i >= 0:
    # 向上再回溯，把包含 vec.emplace_back 的整卡删掉
    ls = t.split("\n")
    s = i
    while s > 0 and 'vec.emplace_back(_strdup(("推荐皮肤")))' not in t.split("\n")[s]:
        if s < i - 30: break
        s -= 1
    if '推荐皮肤' in t.split("\n")[s]:
        # 从 vec 所在的再上层 { 开始
        s2 = s
        while s2 > 0 and not ls[s2].rstrip().endswith("{"):
            s2 -= 1
        del_block(s2, verify="主题")
    else:
        del_block(i)
    print("E8. 主题combo完成")

# ============ F. 局部变量行过滤 ============
ls = t.split("\n")
before = len(ls)
ls = [ln for ln in ls if "int SelectLanguage" not in ln
      and "SelectLanguage == i" not in ln
      and "SelectLanguage = i;" not in ln
      and "setlist.selectLanguage != SelectLanguage" not in ln
      and "setlist.selectLanguage = SelectLanguage;" not in ln
      and "ComponentShortcutButtonRollCall" not in ln
      and "ComponentShortcutButtonLinkage" not in ln
      and "int SetSkinMode" not in ln
      and "SetSkinMode == i" not in ln
      and "SetSkinMode == 0" not in ln
      and "setlist.SetSkinMode != SetSkinMode" not in ln
      and "setlist.SetSkinMode = SetSkinMode;" not in ln
      and "setlist.SetSkinMode = 0" not in ln
      and "setlist.SkinMode = SetSkinMode;" not in ln
      and "bool PptComShowLoadingScreen" not in ln
      and "pptComSetlist.showLoadingScreen = PptComShowLoadingScreen" not in ln]
t = "\n".join(ls)
print(f"F. 局部变量清理 {before - len(ls)}行")

# ============ G. 孤立 else 扫尾 ============
ls = t.split("\n")
deletes = []
for i, ln in enumerate(ls):
    s = ln.strip()
    if s.startswith("else ") and ("en.inkeys.top" in s or "discussions" in s):
        deletes.append(i)
for d in sorted(deletes, reverse=True):
    del ls[d]
t = "\n".join(ls)
print(f"G. 孤立else清理 {len(deletes)}行")

# ============ H. 新开关卡片 ============
smooth = 'ImGui::Toggle("##抬笔平滑笔迹", &SmoothWriting, config);'
if smooth in t and "橡皮快捷清空" not in t:
    si = t.index(smooth)
    end_marker = "ImGui::EndChild();"
    ei = t.index(end_marker, si) + len(end_marker)
    while t[ei - 1] != "}":
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
    print("H1. 橡皮卡片插入")

# 三个 PPT 开关（记忆控件位置卡片后）
memo = 'ImGui::Toggle("##记忆控件位置", &MemoryWidgetPosition, config);'
if memo in t and "是否允许控件拖动位置" not in t:
    def ppt_card(child, var, label):
        return """

									{
										ImGui::SetCursorPosY(ImGui::GetCursorPosY() + 10.0f * settingGlobalScale);
										PushStyleVarNum++, ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0.0f, 0.0f));
										PushStyleVarNum++, ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, 4.0f);
										PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_ChildBg, IM_COL32(251, 251, 251, 255));
										ImGui::BeginChild("%s", { 750.0f * settingGlobalScale,60.0f * settingGlobalScale }, true, ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);

										float cursosPosY = 0;
										{
											ImGui::SetCursorPos({ 20.0f * settingGlobalScale, cursosPosY + 22.0f * settingGlobalScale });
											ImFontMain->Scale = 0.6f, PushFontNum++, ImGui::PushFont(ImFontMain);
											PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0, 0, 0, 255));
											ImGui::TextUnformatted("%s");
										}
										{
											ImGui::SetCursorPos({ 690.0f * settingGlobalScale, cursosPosY + 20.0f * settingGlobalScale });
											PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_FrameBg, IM_COL32(0, 0, 0, 6));
											PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_FrameBgHovered, IM_COL32(0, 0, 0, 15));
											PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Button, IM_COL32(0, 95, 184, 255));
											PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_ButtonHovered, IM_COL32(0, 95, 184, 230));
											if (!%s)
											{
												PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0, 0, 0, 155));
												PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_BorderShadow, IM_COL32(0, 0, 0, 155));
											}
											else
											{
												PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(255, 255, 255, 255));
												PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_BorderShadow, IM_COL32(0, 95, 184, 255));
											}
											ImGui::Toggle("##%s", &%s, config);

											if (pptComSetlist.%s != %s)
											{
												pptComSetlist.%s = %s;
												PptComWriteSetting();
											}
										}

										{
											if (PushStyleColorNum >= 0) ImGui::PopStyleColor(PushStyleColorNum), PushStyleColorNum = 0;
											if (PushStyleVarNum >= 0) ImGui::PopStyleVar(PushStyleVarNum), PushStyleVarNum = 0;
											while (PushFontNum) PushFontNum--, ImGui::PopFont();
										}
										ImGui::EndChild();
									}""" % (child, label, var, label, var,
                                            var[0].lower() + var[1:], var, var[0].lower() + var[1:], var)
    si = t.index(memo)
    end_marker = "ImGui::EndChild();"
    ei = t.index(end_marker, si) + len(end_marker)
    while t[ei - 1] != "}":
        ei = t.index("}", ei) + 1
    cards = (ppt_card("切出放映窗口时自动结束放映", "ExitShowOnFocusLost", "切出放映窗口时自动结束放映")
             + ppt_card("点击中间页码打开大纲视图", "MiddlePageNumOpenOutline", "点击中间页码打开大纲视图")
             + ppt_card("是否允许控件拖动位置", "AllowWidgetDrag", "是否允许控件拖动位置"))
    t = t[:ei] + cards + t[ei:]
    # 局部快照
    anchor = "\t\tbool MemoryWidgetPosition = pptComSetlist.memoryWidgetPosition;"
    if anchor in t and "bool AllowWidgetDrag = pptComSetlist.allowWidgetDrag;" not in t:
        t = t.replace(anchor, anchor + "\n\t\tbool ExitShowOnFocusLost = pptComSetlist.exitShowOnFocusLost;\n\t\tbool MiddlePageNumOpenOutline = pptComSetlist.middlePageNumOpenOutline;\n\t\tbool AllowWidgetDrag = pptComSetlist.allowWidgetDrag;")
    print("H2. PPT三开关插入")

# 分组扩高
ss('BeginChild("绘制#3", { 750.0f * settingGlobalScale,90.0f', 'BeginChild("绘制#3", { 750.0f * settingGlobalScale,160.0f', "绘制#3扩高")
ss('BeginChild("PPT演示助手#4", { 750.0f * settingGlobalScale,155.0f', 'BeginChild("PPT演示助手#4", { 750.0f * settingGlobalScale,420.0f', "PPT#4扩高")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("完成:", t.count("\n"), "行")
print("残余: IA/IW=", t.count("IA(") + t.count("IW("),
      "I18n=", t.count("I18n::"),
      "SkinMode=", t.count("SkinMode"),
      "SetSkinMode=", t.count("SetSkinMode"),
      "SelectLanguage=", t.count("SelectLanguage"),
      "马年=", t.count("马年迎新"),
      "社区名片=", t.count("社区名片"))
