import io, os

os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

# ===== 1. IdtSetting.cpp =====
p = "IdtSetting.cpp"
lines = io.open(p, encoding="utf-8", newline="").read().split("\n")

# 1a. 删除孤立局部
i = next(i for i, ln in enumerate(lines) if ln.strip() == "int SetSkinMode = 0;")
del lines[i]
print("1a. 孤立 SetSkinMode 局部已删（行", i + 1, "）")

# 1b. 加拖动开关卡片到 #4 分组（在 大纲视图 卡片之后）
idx = next(i for i, ln in enumerate(lines) if 'BeginChild("点击中间页码打开大纲视图"' in ln)
# 找该卡片的包裹块结束（EndChild 后的 \t\t\t\t\t}）
j = idx
while "ImGui::EndChild();" not in lines[j]:
    j += 1
while lines[j].rstrip() != "\t\t\t\t\t}":
    j += 1

def toggle_card(child_name, var_name, label):
    I = "\t\t\t\t\t"
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

card = toggle_card("是否允许控件拖动位置", "AllowWidgetDrag", "是否允许控件拖动位置").split("\n")
lines[j + 1:j + 1] = card
print("1b. 拖动开关卡片已插入")

# 1c. #4 分组扩高 155 -> 450
for i, ln in enumerate(lines):
    if 'BeginChild("PPT演示助手#4"' in ln and "155.0f" in ln:
        lines[i] = ln.replace("155.0f", "450.0f")
        print("1c. #4 分组 155 -> 450")
        break

# 1d. 拖动局部快照
k = next(i for i, ln in enumerate(lines) if "bool ExitShowOnFocusLost = pptComSetlist.exitShowOnFocusLost;" in ln)
lines[k + 1:k + 1] = ["\t\tbool AllowWidgetDrag = pptComSetlist.allowWidgetDrag;"]
print("1d. 局部快照 OK")

io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))

# ===== 2. rc：删 SKIN1；删 dragon.png =====
p = "AnyThingDraw.rc"
t = io.open(p, encoding="utf-8", newline="").read()
a = 'SKIN1                   PNG                     "src\\\\skin\\\\dragon.png"\n'
assert a in t, "rc SKIN1"
t = t.replace(a, "")
io.open(p, "w", encoding="utf-8", newline="").write(t)
os.remove("src/skin/dragon.png")
print("2. SKIN1 与 dragon.png 已删")
