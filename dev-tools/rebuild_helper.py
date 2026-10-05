import io, os, re, json

os.chdir(r"D:\开发\AnythingDraw\Inkeys")

# ===== 1. zh-CN 文案映射（从 git HEAD 的 jsonc 取，因为工作区 jsonc 已删） =====
import subprocess
raw = subprocess.run(["git", "show", "HEAD:智绘教/src/i18n/zh-CN.jsonc"],
                     capture_output=True, check=True).stdout.decode("utf-8-sig")
jl = [ln for ln in raw.split("\n") if not ln.lstrip().startswith("//")]
data = json.loads("\n".join(jl))
flat = {}
def flatten(o, pre):
    for k, v in o.items():
        path = (pre + "/" + k) if pre else k
        if isinstance(v, dict):
            flatten(v, path)
        else:
            flat[path] = v
flatten(data, "")
print("文案键:", len(flat))

def esc(v):
    return v.replace("\\", "\\\\").replace('"', '\\"').replace("\r", "\\r").replace("\n", "\\n")

# ===== 2. 提取 HEAD 主栏块 =====
head = subprocess.run(["git", "show", "HEAD:智绘教/IdtSetting.cpp"],
                      capture_output=True, check=True).stdout.decode("utf-8-sig", errors="replace")
hl = head.split("\n")
anchor = next(i for i, ln in enumerate(hl) if 'BeginChild("PPT演示助手主栏"' in ln)
wstart = anchor
while wstart > 0 and hl[wstart].rstrip() not in ("\t\t\t\t{", "\t\t\t\t\t{"):
    wstart -= 1
depth = 0
seen = False
wend = None
j = wstart
while j < len(hl):
    k = 0
    in_str = False
    while k < len(hl[j]):
        c = hl[j][k]
        if in_str:
            if c == "\\":
                k += 2
                continue
            if c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif hl[j][k:k+2] == "//":
                break
            elif c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
        k += 1
    if seen and depth == 0:
        wend = j
        break
    seen = seen or "{" in hl[j]
assert wend, "主栏块未配平"
block = hl[wstart:wend + 1]
print("主栏块:", wstart + 1, "-", wend + 1, f"({len(block)}行)")

# ===== 3. 内联 IA/IW =====
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
# 字面量拼接后的 .c_str() 清理
block_t = re.sub(r'(L?"(?:[^"\\]|\\.)*")\.c_str\(\)', r"\1", block_t)
print("IA/IW 残留:", len(re.findall(r"\b(?:IA|IW)\(", block_t)), "缺键:", miss[:5])

# ===== 4. 块内修改 =====
# 4a. 删除 显示加载页面 开关卡片
bl = block_t.split("\n")
idx = next(i for i, ln in enumerate(bl) if 'BeginChild("显示加载页面"' in ln)
s = idx
while s > 0 and bl[s].rstrip() not in ("\t\t\t\t\t\t{", "\t\t\t\t\t{", "\t\t\t\t{"):
    s -= 1
depth = 0
seen = False
end = None
j = s
while j < len(bl):
    depth += bl[j].count("{") - bl[j].count("}")
    if "{" in bl[j]:
        seen = True
    if seen and depth == 0:
        end = j
        break
    j += 1
del bl[s:end + 1]
block_t = "\n".join(bl)
print("4a. 加载页面卡片已删")

# 4b. 控件位置 -> 控件设置
block_t = block_t.replace('ImGui::TextUnformatted("控件位置");', 'ImGui::TextUnformatted("控件设置");')

# 4c. 记忆控件位置卡片后插入三个新开关卡片
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
# 记忆卡片块结束：向后找 EndChild 后的 \t\t\t\t\t\t}（卡片包裹）
j = midx
while "ImGui::EndChild();" not in bl[j]:
    j += 1
while bl[j].rstrip() != "\t\t\t\t\t\t}":
    j += 1
new_cards = (toggle_card("切出放映窗口时自动结束放映", "ExitShowOnFocusLost", "切出放映窗口时自动结束放映", "\t\t\t\t\t\t") +
             toggle_card("点击中间页码打开大纲视图", "MiddlePageNumOpenOutline", "点击中间页码打开大纲视图", "\t\t\t\t\t\t") +
             toggle_card("是否允许控件拖动位置", "AllowWidgetDrag", "是否允许控件拖动位置", "\t\t\t\t\t\t")).split("\n")
bl[j + 1:j + 1] = new_cards
block_t = "\n".join(bl)

# 4d. 控件位置组容器扩高（找到包着 重置控件位置 的组容器，高度加大）
bl = block_t.split("\n")
for i, ln in enumerate(bl):
    if 'BeginChild("PPT演示助手#4"' in ln:
        bl[i] = ln.replace("155.0f", "420.0f")
        print("4d. #4 分组扩到 420")
        break
block_t = "\n".join(bl)

# ===== 5. 插回当前文件 =====
p = "IdtSetting.cpp"
cl = io.open(p, encoding="utf-8", newline="").read().split("\n")
# 插入点： pops 块之前（PPT助手子页壳的 pops）
ins = next(i for i, ln in enumerate(cl) if i > 4600 and "PushStyleColorNum >= 0" in ln and cl[i-3:i-1].__str__().find("4706") >= 0) if False else None
# 直接找：PPT助手壳的 pops（在 break; 前的那个）——用 4715 break 行定位
brk = 4715  # 当前 break 行
# 从 break 行向上找 pops 块的 {
k = brk - 1
while k > 0 and not (cl[k].rstrip() == "\t\t\t\t{" ):
    if "PushStyleColorNum >= 0" in cl[k]:
        popline = k
    k -= 1
# pops 块起点 = popline 上方的 { 行
ins_at = popline
while cl[ins_at - 1].strip() == "":
    ins_at -= 1
# ins_at 现在是 pops { 行；在其前插入
cl[ins_at:ins_at] = block_t.split("\n") + [""]
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(cl))
print("5. 主栏块已插回 IdtSetting.cpp")
