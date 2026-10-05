import io, os

os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

# ========== A. IdtConfiguration.h ==========
p = "IdtConfiguration.h"
t = io.open(p, encoding="utf-8", newline="").read()
a = "\t\texitShowOnFocusLost = true;"
assert a in t
t = t.replace(a, a + "\n\t\tallowWidgetDrag = false;")
a2 = "\t// 切出放映窗口时自动结束放映\n\tbool exitShowOnFocusLost;"
assert a2 in t
t = t.replace(a2, a2 + "\n\t// 是否允许控件拖动位置\n\tbool allowWidgetDrag;")
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("A OK")

# ========== B. IdtConfiguration.cpp ==========
p = "IdtConfiguration.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
a = '\t\tif (updateVal.isMember("ExitShowOnFocusLost") && updateVal["ExitShowOnFocusLost"].isBool())\n\t\t\tpptComSetlist.exitShowOnFocusLost = updateVal["ExitShowOnFocusLost"].asBool();'
assert a in t
t = t.replace(a, a + '\n\t\tif (updateVal.isMember("AllowWidgetDrag") && updateVal["AllowWidgetDrag"].isBool())\n\t\t\tpptComSetlist.allowWidgetDrag = updateVal["AllowWidgetDrag"].asBool();')
a2 = '\t\tupdateVal["ExitShowOnFocusLost"] = Json::Value(pptComSetlist.exitShowOnFocusLost);'
assert a2 in t
t = t.replace(a2, a2 + '\n\t\tupdateVal["AllowWidgetDrag"] = Json::Value(pptComSetlist.allowWidgetDrag);')
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("B OK")

# ========== C. IdtPlug-in.cpp：拖动开关 ==========
p = "IdtPlug-in.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
a = """				if (m.message == WM_LBUTTONDOWN)
					{
						PptBottomMiddleSeekBar(m.x, m.y);"""
assert a in t, "drag call"
t = t.replace(a, """				if (m.message == WM_LBUTTONDOWN && pptComSetlist.allowWidgetDrag)
					{
						PptBottomMiddleSeekBar(m.x, m.y);""")
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("C OK")

# ========== D. IdtFloating.cpp：删龙年迎新分支 + skin[1] 加载 ==========
p = "IdtFloating.cpp"
lines = io.open(p, encoding="utf-8", newline="").read().split("\n")
start = next(i for i, ln in enumerate(lines) if "//龙年迎新" in ln)
# start 指向 else if 行的上一行注释；else if 在 start+1
assert "else if (setlist.SkinMode == 3)" in lines[start + 1]
depth = 0
seen = False
end = None
for j in range(start + 1, len(lines)):
    depth += lines[j].count("{") - lines[j].count("}")
    if "{" in lines[j]:
        seen = True
    if seen and depth == 0:
        end = j
        break
assert end is not None
del lines[start:end + 1]
t = "\n".join(lines)
a = '\t\t\tidtLoadImage(&skin[1], L"PNG", L"skin1");\n'
assert a in t
t = t.replace(a, "")
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("D OK（龙年迎新分支与 skin1 加载已删）")

# ========== E. IdtSetting.cpp：选项删除 + 快照 + 开关卡片 ==========
p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
a = '\t\t\t\t\t\t\t\t\t\tvec.emplace_back(_strdup(("马年迎新")));'
assert a in t
t = t.replace(a, "")
a = "\t\tbool ExitShowOnFocusLost = pptComSetlist.exitShowOnFocusLost;"
assert a in t
t = t.replace(a, a + "\n\t\tbool AllowWidgetDrag = pptComSetlist.allowWidgetDrag;")

anchor = 'ImGui::BeginChild("切出放映窗口时自动结束放映", { 750.0f * settingGlobalScale,60.0f * settingGlobalScale }, true, ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);'
idx = t.index(anchor)
end_idx = t.index("ImGui::EndChild();", idx)
close_idx = t.index("\t\t\t\t\t}", end_idx)
close_idx = t.index("\n", close_idx) + 1

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

pre = t[:close_idx]
post = t[close_idx:]
pre += toggle_card("是否允许控件拖动位置", "AllowWidgetDrag", "是否允许控件拖动位置")
t = pre + post

# #4 分组高度 300 -> 450（容纳第四张卡片）
a = 'ImGui::BeginChild("PPT演示助手#4", { 750.0f * settingGlobalScale,300.0f * settingGlobalScale }, false, ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);'
assert a in t
t = t.replace(a, a.replace("300.0f", "450.0f"))
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("E OK")

# ========== F. rc：删 SKIN1 + 删 dragon.png ==========
p = "AnyThingDraw.rc"
t = io.open(p, encoding="utf-8", newline="").read()
a = 'SKIN1                   PNG                     "src\\\\skin\\\\dragon.png"\n'
assert a in t
t = t.replace(a, "")
io.open(p, "w", encoding="utf-8", newline="").write(t)
os.remove("src/skin/dragon.png")
print("F OK（SKIN1 条目与 dragon.png 已删）")
