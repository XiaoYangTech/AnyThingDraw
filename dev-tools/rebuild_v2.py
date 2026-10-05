import io, os, re, json, subprocess, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys")

def git_show(path):
    return subprocess.run(["git", "show", "HEAD:" + path], capture_output=True, timeout=30, check=True).stdout.decode("utf-8-sig", errors="replace")

# ===== 文案映射 =====
raw = git_show("智绘教/src/i18n/zh-CN.jsonc")
jl = [ln for ln in raw.split("\n") if not ln.lstrip().startswith("//")]
data = json.loads("\n".join(jl))
flat = {}
def fl(o, pre):
    for k, v in o.items():
        pp = (pre + "/" + k) if pre else k
        if isinstance(v, dict):
            fl(v, pp)
        else:
            flat[pp] = v
fl(data, "")

def esc(v):
    return v.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n")

def depth_delta(line):
    d = 0
    in_str = False
    i = 0
    while i < len(line):
        c = line[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif line[i:i+2] == "//":
                break
            elif c == "{":
                d += 1
            elif c == "}":
                d -= 1
        i += 1
    return d

# ===== 提取 HEAD 主栏块 =====
head = git_show("智绘教/IdtSetting.cpp")
hl = head.split("\n")
# HEAD 中 主栏 BeginChild 行
anchor = next(i for i, ln in enumerate(hl) if 'BeginChild("PPT演示助手主栏"' in ln)
# 块起点：BeginChild 所在的包裹块 — 用 BeginChild 行本身作为块首（含缩进的 BeginChild 行）
bstart = anchor
# 块终点：从 anchor 起配平（BeginChild 行含 { 750,555 } 同行配平，所以从 anchor+1 起算内容深度）
# 终点：超级置顶页容器（下一子页）之前最后一个 EndChild
super_idx = next(i for i, ln in enumerate(hl) if i > anchor and 'BeginChild("超级置顶", { (750' in ln)
bend = max(j for j in range(anchor, super_idx) if 'ImGui::EndChild();' in hl[j])
block = hl[anchor:bend + 1]
print("主栏块:", anchor + 1, "-", bend + 1, f"({len(block)}行)")

# ===== 内联 IA/IW =====
block_t = "\n".join(block)
miss = []
def rep_ia(m):
    kind, key = m.group(1), m.group(2)
    v = flat.get(key)
    if v is None:
        miss.append(key)
        return m.group(0)
    return ('L"' if kind == "IW" else '"') + esc(v) + '"'
block_t = re.sub(r'\b(IA|IW)\("([^"]+)"\)', rep_ia, block_t)
block_t = re.sub(r'(L?"(?:[^"\\]|\\.)*")\.c_str\(\)', r"\1", block_t)
print("IA/IW 残留:", len(re.findall(r"\b(?:IA|IW)\(", block_t)), "| 缺键:", len(miss))

# ===== 删除 显示加载页面 开关卡片 =====
bl = block_t.split("\n")
idx = next(i for i, ln in enumerate(bl) if 'BeginChild("显示加载页面"' in ln)
depth = 0
seen = False
end = None
j = idx
while j < len(bl):
    depth += depth_delta(bl[j])
    if "{" in bl[j]:
        seen = True
    if seen and depth == 0:
        end = j
        break
    j += 1
del bl[idx:end + 1]
block_t = "\n".join(bl)
print("加载页面卡片已删")

# ===== 控件位置 -> 控件设置 =====
block_t = block_t.replace('ImGui::TextUnformatted("控件位置");', 'ImGui::TextUnformatted("控件设置");')

# ===== 记忆控件位置卡片后插三个新开关 =====
def toggle_card(child_name, var_name, label, I):
    I2 = I + "\t"
    I3 = I2 + "\t"
    I4 = I3 + "\t"
    s = "\n" + I + "{\n"
    s += I2 + "ImGui::SetCursorPosY(ImGui::GetCursorPosY() + 10.0f * settingGlobalScale);\n"
    s += I2 + "PushStyleVarNum++, ImGui::PushStyleVar(ImGuiStyleVar_WindowPadding, ImVec2(0.0f, 0.0f));\n"
    s += I2 + "PushStyleVarNum++, ImGui::PushStyleVar(ImGuiStyleVar_ChildRounding, 4.0f);\n"
    s += I2 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_ChildBg, IM_COL32(251, 251, 251, 255));\n"
    s += I2 + f'ImGui::BeginChild("{child_name}", {{ 750.0f * settingGlobalScale,60.0f * settingGlobalScale }}, true, ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);\n'
    s += "\n" + I2 + "float cursosPosY = 0;\n"
    s += I2 + "{\n"
    s += I3 + 'ImGui::SetCursorPos({ 20.0f * settingGlobalScale, cursosPosY + 22.0f * settingGlobalScale });\n'
    s += I3 + "ImFontMain->Scale = 0.6f, PushFontNum++, ImGui::PushFont(ImFontMain);\n"
    s += I3 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0, 0, 0, 255));\n"
    s += I3 + f'ImGui::TextUnformatted("{label}");\n'
    s += I2 + "}\n"
    s += I2 + "{\n"
    s += I3 + 'ImGui::SetCursorPos({ 690.0f * settingGlobalScale, cursosPosY + 20.0f * settingGlobalScale });\n'
    s += I3 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_FrameBg, IM_COL32(0, 0, 0, 6));\n"
    s += I3 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_FrameBgHovered, IM_COL32(0, 0, 0, 15));\n"
    s += I3 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Button, IM_COL32(0, 95, 184, 255));\n"
    s += I3 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_ButtonHovered, IM_COL32(0, 95, 184, 230));\n"
    s += I3 + f"if (!{var_name})\n"
    s += I3 + "{\n"
    s += I4 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(0, 0, 0, 155));\n"
    s += I4 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_BorderShadow, IM_COL32(0, 0, 0, 155));\n"
    s += I3 + "}\n"
    s += I3 + "else\n"
    s += I3 + "{\n"
    s += I4 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_Text, IM_COL32(255, 255, 255, 255));\n"
    s += I4 + "PushStyleColorNum++, ImGui::PushStyleColor(ImGuiCol_BorderShadow, IM_COL32(0, 95, 184, 255));\n"
    s += I3 + "}\n"
    s += I3 + f'ImGui::Toggle("##{label}", &{var_name}, config);\n'
    s += "\n"
    s += I3 + f"if (pptComSetlist.{var_name[0].lower() + var_name[1:]} != {var_name})\n"
    s += I3 + "{\n"
    s += I4 + f"pptComSetlist.{var_name[0].lower() + var_name[1:]} = {var_name};\n"
    s += I4 + "PptComWriteSetting();\n"
    s += I3 + "}\n"
    s += I2 + "}\n"
    s += "\n" + I2 + "{\n"
    s += I3 + "if (PushStyleColorNum >= 0) ImGui::PopStyleColor(PushStyleColorNum), PushStyleColorNum = 0;\n"
    s += I3 + "if (PushStyleVarNum >= 0) ImGui::PopStyleVar(PushStyleVarNum), PushStyleVarNum = 0;\n"
    s += I3 + "while (PushFontNum) PushFontNum--, ImGui::PopFont();\n"
    s += I2 + "}\n"
    s += I2 + "ImGui::EndChild();\n"
    s += I + "}\n"
    return s

bl = block_t.split("\n")
midx = next(i for i, ln in enumerate(bl) if 'Toggle("##记忆控件位置"' in ln)
j = midx
while "ImGui::EndChild();" not in bl[j]:
    j += 1
while bl[j].rstrip() != "\t\t\t\t\t\t}":
    j += 1
cards = (toggle_card("切出放映窗口时自动结束放映", "ExitShowOnFocusLost", "切出放映窗口时自动结束放映", "\t\t\t\t\t\t") +
         toggle_card("点击中间页码打开大纲视图", "MiddlePageNumOpenOutline", "点击中间页码打开大纲视图", "\t\t\t\t\t\t") +
         toggle_card("是否允许控件拖动位置", "AllowWidgetDrag", "是否允许控件拖动位置", "\t\t\t\t\t\t")).split("\n")
bl[j + 1:j + 1] = cards
block_t = "\n".join(bl)

# ===== 插入当前文件：主取消息壳的 pops 前不行——插在 PPT助手子页 EndChild 之前 =====
p = "AnyThingDraw/IdtSetting.cpp"
cl = io.open(p, encoding="utf-8", newline="").read().split("\n")
# 当前 PPT助手子页：导航+标题后、pops 前的插入点 = break 行(4715→现偏移) 上方的 EndChild 行
# 锚定：子页壳的 EndChild 与 break —— 从子页标题"PPT演示助手"(TextUnformatted) 向后找
title_idx = next(i for i, ln in enumerate(cl) if i > 4000 and 'TextUnformatted("PPT演示助手")' in ln)
eidx = next(i for i, ln in enumerate(cl) if i > title_idx and ln.strip() == "ImGui::EndChild();")
# eidx 即子页容器的 EndChild；块插在它之前
cl[eidx:eidx] = block_t.split("\n")
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(cl))
print("主栏块已插回（插入于", eidx + 1, "行前）")
