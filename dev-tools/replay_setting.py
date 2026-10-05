import io, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
orig_len = len(t)
print("初始:", len(t), "字节")

def sub_assert(a, b, tag):
    global t
    if a not in t:
        print(f"  跳过 {tag} (无匹配)")
        return
    t = t.replace(a, b)

def sub_all(a, b, tag):
    global t
    n = t.count(a)
    if n == 0:
        print(f"  跳过 {tag} (count=0)")
        return
    t = t.replace(a, b)
    print(f"{tag}: {n}处")

# ===== 第一轮：品牌 =====
sub_all("Inkeys", "AnyThingDraw", "Inkeys→AnyThingDraw")
sub_all("inkeys3", "anythingdraw3", "inkeys3")



# ===== 第二轮：品牌补充 + i18n 内联 =====
sub_all("import Inkeys.Thread.Status", "import AnyThingDraw.Thread.Status", "import")
# IdtI18n include 移除
t = t.replace('#include "IdtI18n.h"\n', "")

# ===== 第三轮：去品牌后文本修正 =====
# 提示标题
sub_all('L"Inkeys Tips | 智绘教提示"', 'L"AnyThingDraw Tips | 亿方万能画笔提示"', "tips title")
sub_all('L"Inkeys Error | 智绘教错误"', 'L"AnyThingDraw Error | 亿方万能画笔错误"', "error title")

# ===== 第四轮：i18n 系统删除（IA/IW 内联） =====
# 1a. SkinMode==3 块删除（注释+块，配平）
lines = t.split("\n")
removed = 0
i = 0
while i < len(lines):
    if "else if (setlist.SkinMode == 3)" in lines[i]:
        cstart = i
        while cstart > 0 and lines[cstart - 1].strip().startswith("//"):
            cstart -= 1
        depth = 0
        seen = False
        end = None
        for j in range(i, len(lines)):
            depth += lines[j].count("{") - lines[j].count("}")
            if "{" in lines[j]:
                seen = True
            if seen and depth == 0:
                end = j
                break
        del lines[cstart:end + 1]
        removed += 1
        continue
    i += 1
t = "\n".join(lines)
print("SkinMode==3 块删除:", removed)

# 1b. SkinMode 条件常量化
t = t.replace("(setlist.SkinMode == 1 || setlist.SkinMode == 2)", "(true)")
t = t.replace("setlist.SkinMode == 1", "true")
# 1c. SkinMode==2 块删除
lines = t.split("\n")
removed = 0
i = 0
while i < len(lines):
    if "else if (setlist.SkinMode == 2)" in lines[i]:
        depth = 0
        seen = False
        end = None
        for j in range(i, len(lines)):
            depth += lines[j].count("{") - lines[j].count("}")
            if "{" in lines[j]:
                seen = True
            if seen and depth == 0:
                end = j
                break
        del lines[i:end + 1]
        removed += 1
        continue
    i += 1
t = "\n".join(lines)
print("SkinMode==2 块删除:", removed)

# 1d. skin[1]/skin[3]/bskin3 清理
for a in [
    '\t\t\tidtLoadImage(&skin[1], L"PNG", L"skin1");\n',
    '\t\t\tidtLoadImage(&skin[3], L"PNG", L"skin1-3");\n',
    "\t\t\tbskin3 = IMAGEToBitmap(&skin[3]);\n",
    "\tBitmap* bskin3;\n",
]:
    if a in t:
        t = t.replace(a, "")

# 1e. skin[3]/bskin3 残余引用行删除
lines = t.split("\n")
i = 0
while i < len(lines):
    if ("skin[3]" in lines[i] or "bskin3" in lines[i]) and "skin[2]" not in lines[i]:
        del lines[i]
        continue
    i += 1
t = "\n".join(lines)

# ===== 第五轮：i18n 全量内联（IA/IW → 中文） =====
# 从 git HEAD 的 zh-CN.jsonc 获取映射
import subprocess, json
raw = subprocess.run(["git", "show", "HEAD:智绘教/src/i18n/zh-CN.jsonc"], capture_output=True, check=True).stdout.decode("utf-8-sig")
jl = [ln for ln in raw.split("\n") if not ln.lstrip().startswith("//")]
data = json.loads("\n".join(jl))
flat = {}
def flatten(o, pre):
    for k, v in o.items():
        pp = (pre + "/" + k) if pre else k
        if isinstance(v, dict):
            flatten(v, pp)
        else:
            flat[pp] = v
flatten(data, "")

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
# .c_str() 清理
t = re.sub(r'(L?"(?:[^"\\]|\\.)*")\.c_str\(\)', r"\1", t)
# 字面量+字面量合并
for _ in range(8):
    n1 = len(re.findall(r'(L?"(?:[^"\\]|\\.)*")\s*\+\s*(L?"(?:[^"\\]|\\.)*")', t))
    t = re.sub(r'(L?"(?:[^"\\]|\\.)*")\s*\+\s*(L?"(?:[^"\\]|\\.)*")', r"\1\2", t)
    if n1 == 0:
        break
print("i18n 内联完成, 缺键:", miss[:3], "残留IA/IW:", len(re.findall(r"\b(?:IA|IW)\(", t)))

# ===== 第六轮：块删除 =====
def del_brace_block(lines, start_comment, end_anchor):
    """删除从 start_comment 注释行起到 end_anchor 行（不含）的所有行"""
    si = next(i for i, ln in enumerate(lines) if start_comment in ln)
    ei = next(i for i, ln in enumerate(lines) if end_anchor in ln)
    del lines[si:ei]

# 社区名片
del_brace_block(lines, "// 社区名片", "// 赞助我们")
# 点名器/ClassIsland 组件
try:
    si = next(i for i, ln in enumerate(lines) if "BeginChild(\"组件#4\"" in ln)
    ei = next(i for i, ln in enumerate(lines) if "BeginChild(\"PPT演示助手-介绍\"" in ln and i > si + 500)
    del lines[si:ei]
except StopIteration:
    print("  跳过 点名器块 (锚点未找到)")
# 更新渠道
try:
    si = next(i for i, ln in enumerate(lines) if '"LimitUpdate"' in ln)
    ei = next(i for i, ln in enumerate(lines) if '"Inkeys3Update"' in ln or '"AnyThingDraw3Update"' in ln)
    del lines[si:ei]
except StopIteration:
    print("  跳过 更新渠道块")
# 历史画布保存
try:
    si = next(i for i, ln in enumerate(lines) if "配置保存#2" in ln)
except StopIteration:
    si = None
if si is not None:
# 找配平
depth = 0
seen = False
ei = None
for j in range(si, len(lines)):
    depth += lines[j].count("{") - lines[j].count("}")
    if "{" in lines[j]:
        seen = True
    if seen and depth == 0:
        ei = j
        break
del lines[si:ei + 1]
# 主页 QQ 号
si = next(i for i, ln in enumerate(lines) if 'TextUnformatted("2685549821")' in ln)
# 向上到 { 开始
k = si
while lines[k].rstrip() != "{":
    k -= 1
depth = 0
seen = False
ei = None
for j in range(k, len(lines)):
    depth += lines[j].count("{") - lines[j].count("}")
    if "{" in lines[j]:
        seen = True
    if seen and depth == 0:
        ei = j
        break
del lines[k:ei + 1]
# 加载页面开关
si = next(i for i, ln in enumerate(lines) if 'BeginChild("显示加载页面"' in ln)
depth = 0
seen = False
ei = None
for j in range(si, len(lines)):
    depth += lines[j].count("{") - lines[j].count("}")
    if "{" in lines[j]:
        seen = True
    if seen and depth == 0:
        ei = j
        break
del lines[si:ei + 1]
print("块删除完成")

# ===== 第七轮：控件位置→控件设置、语言tab删除 =====
sub_all('ImGui::TextUnformatted("控件位置");', 'ImGui::TextUnformatted("控件设置");', "控件设置")
# 语言tab块删除（通过 settingTabEnum::Language）
si = next(i for i, ln in enumerate(lines) if "case settingTabEnum::Language:" in ln)
depth = 0
seen = False
ei = None
for j in range(si, len(lines)):
    depth += lines[j].count("{") - lines[j].count("}")
    if "{" in lines[j]:
        seen = True
    if seen and depth == 0:
        ei = j
        break
del lines[si:ei + 1]
# 语言导航按钮
for i, ln in enumerate(lines):
    if "settingTab = settingTabEnum::Language;" in ln:
        # 向上找包裹 {
        k = i
        while lines[k].rstrip() != "{":
            k -= 1
        # 向下找 }
        e = i
        while lines[e].rstrip() != "}":
            e += 1
        del lines[k:e + 1]
        break
print("语言tab删除完成")

# ===== 第八轮：文本替换 =====
sub_all('L"选择(清空)"', 'L"选择并清空"', "选择并清空")
sub_all('L"画笔"', 'L"批注"', "批注")
sub_all('L"选项"', 'L"设置"', "设置")
sub_all('L"定格"', 'L"冻屏"', "冻屏")
sub_all('L"穿透"', 'L"鼠标"', "鼠标")
sub_all('ImGui::TextUnformatted("控件位置");', 'ImGui::TextUnformatted("控件设置");', "控件设置")

# ===== 第九轮：版本、快捷方式、插件名 =====
sub_all('L"\\n软件发布版本 " + (editionDate.length() >= 8 ? editionDate.substr(0, 4) + L"年" + editionDate.substr(4, 2) + L"月" + editionDate.substr(6, 2) + L"日" : editionDate) + L"（" + editionChannel + L"）"',
        'L"\\n软件发布版本 1.0.0"', "版本")
t = t.replace("亿方万能画笔(屏幕批注工具).lnk", "亿方万能画笔.lnk")
t = t.replace("PPT演示助手 3 轻量版", "PPT演示助手")
t = t.replace("同类软件悬浮窗拦截助手 3 轻量版", "同类软件悬浮窗拦截助手")

# ===== 第十轮：新开关 =====
# PPT助手三个开关已在第六轮块操作中处理过（如果在此文件中）
# 橡皮开关卡片：在 抬笔平滑笔迹 Toggle 后插入
smooth_toggle = 'ImGui::Toggle("##抬笔平滑笔迹", &SmoothWriting, config);'
if smooth_toggle in t:
    after_write = """if (setlist.smoothWriting != SmoothWriting)
								{
									setlist.smoothWriting = SmoothWriting;
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
    card = after_write + """

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
    # 只替换第一个出现的 after_write + card 组合
    idx = t.index(after_write)
    # 找到 after_write 后第一个出现的完整写盘块和卡片结束
    end_marker = "ImGui::EndChild();\n\t\t\t\t\t}"
    end_idx = t.index(end_marker, idx) + len(end_marker)
    # 在其后插入新卡片
    insert_pos = end_idx
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
    t = t[:insert_pos] + new_card + t[insert_pos:]
    print("橡皮卡片插入 OK")

# ===== 检查 =====
print("残留检查:")
for pat in ["IA(", "IW(", "SetSkinMode", "setlist.SkinMode", "showLoadingScreen", "马年迎新", "推荐皮肤"]:
    c = t.count(pat)
    if c:
        print(f"  {pat}: {c}")

wr = io.open(p, "w", encoding="utf-8", newline="")
wr.write(t)
wr.close()
print("写入完成:", len(t), "字节")
