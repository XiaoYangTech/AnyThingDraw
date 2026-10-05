import io, os

os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

# ===== 1. IdtConfiguration.h：成员 =====
p = "IdtConfiguration.h"
t = io.open(p, encoding="utf-8", newline="").read()
a = "\tbool smoothWriting;\n"
assert a in t
t = t.replace(a, a + "\t// 双击或右键橡皮快速清空并切回批注\n\tbool eraserQuickClean;\n")
wr = io.open(p, "w", encoding="utf-8", newline=""); wr.write(t); wr.close()
print("1. header OK")

# ===== 2. IdtConfiguration.cpp：读写 =====
p = "IdtConfiguration.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
a = '\t\t\tsetlist.smoothWriting = setlistVal["SmoothWriting"].asBool();'
assert a in t
t = t.replace(a, a + '\n\t\tif (setlistVal.isMember("EraserQuickClean") && setlistVal["EraserQuickClean"].isBool())\n\t\t\tsetlist.eraserQuickClean = setlistVal["EraserQuickClean"].asBool();')
a2 = '\tsetlistVal["SmoothWriting"] = Json::Value(setlist.smoothWriting);'
assert a2 in t
t = t.replace(a2, a2 + '\n\tsetlistVal["EraserQuickClean"] = Json::Value(setlist.eraserQuickClean);')
wr = io.open(p, "w", encoding="utf-8", newline=""); wr.write(t); wr.close()
print("2. config IO OK")

# ===== 3. IdtMain.cpp：默认值 =====
p = "IdtMain.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
a = "\t\t\t\tsetlist.smoothWriting = false;"
assert a in t
t = t.replace(a, a + "\n\t\t\t\tsetlist.eraserQuickClean = true;")
wr = io.open(p, "w", encoding="utf-8", newline=""); wr.write(t); wr.close()
print("3. default OK")

# ===== 4. IdtFloating.cpp：双击/右键实现（带开关） =====
p = "IdtFloating.cpp"
t = io.open(p, encoding="utf-8", newline="").read()

a = "\tint brush_connect = -1;"
assert a in t
t = t.replace(a, a + "\n\tstd::chrono::steady_clock::time_point lastEraserClickTime{};")

a = """								if (!m.lbutton)
								{
									state = 1;
									if (stateMode.StateModeSelect != StateModeSelectEnum::IdtEraser) ChangeStateModeToEraser();

									break;
								}"""
b = """								if (!m.lbutton)
								{
									state = 1;

									auto now = std::chrono::steady_clock::now();
									bool doubleClick = (std::chrono::duration_cast<std::chrono::milliseconds>(now - lastEraserClickTime).count() < 400);
									lastEraserClickTime = now;

									if (doubleClick && setlist.eraserQuickClean)
									{
										// 双击橡皮：清空画布并切回批注模式
										ChangeStateModeToSelection();
										for (int i = 0; i < 20 && stateMode.StateModeSelectEcho != StateModeSelectEnum::IdtSelection; i++) std::this_thread::sleep_for(std::chrono::milliseconds(10));
										ChangeStateModeToPen();
									}
									else if (stateMode.StateModeSelect != StateModeSelectEnum::IdtEraser) ChangeStateModeToEraser();

									break;
								}"""
assert t.count(a) == 1, "eraser release block"
t = t.replace(a, b)

a = """					if (m.message == WM_RBUTTONDOWN && setlist.RightClickClose)
					{"""
b = """					// 右键橡皮：清空画布并切回批注模式
					if (m.message == WM_RBUTTONDOWN && setlist.eraserQuickClean && IsInRect(m.x, m.y, { 192 + 8, floating_windows.height - 156 + 8, 192 + 8 + 80, floating_windows.height - 156 + 8 + 80 }))
					{
						ChangeStateModeToSelection();
						for (int i = 0; i < 20 && stateMode.StateModeSelectEcho != StateModeSelectEnum::IdtSelection; i++) std::this_thread::sleep_for(std::chrono::milliseconds(10));
						ChangeStateModeToPen();

						hiex::flushmessage_win32(EM_MOUSE, floating_window);

						MouseInteractionManipulated = std::chrono::high_resolution_clock::now();
					}
					else if (m.message == WM_RBUTTONDOWN && setlist.RightClickClose)
					{"""
assert t.count(a) == 1, "right click anchor"
t = t.replace(a, b)
wr = io.open(p, "w", encoding="utf-8", newline=""); wr.write(t); wr.close()
print("4. eraser interaction OK")

# ===== 5. IdtSetting.cpp：本地快照 + 开关卡片 + 控件设置改名 =====
p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()

a = "\t\tbool SmoothWriting = setlist.smoothWriting;"
assert a in t
t = t.replace(a, a + "\n\t\tbool EraserQuickClean = setlist.eraserQuickClean;")

# 开关卡片：插到 绘制#3 块（抬笔平滑）之后
a = """							ImGui::Toggle("##抬笔平滑笔迹", &SmoothWriting, config);

								if (setlist.smoothWriting != SmoothWriting)
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
						}
"""
assert a in t, "smooth card not found"
card = """							ImGui::Toggle("##抬笔平滑笔迹", &SmoothWriting, config);

								if (setlist.smoothWriting != SmoothWriting)
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
						}

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
						}
"""
t = t.replace(a, card)

# 控件位置 -> 控件设置（PPT助手页分组标题）
a = 'ImGui::TextUnformatted("控件位置");'
assert a in t
t = t.replace(a, 'ImGui::TextUnformatted("控件设置");')

wr = io.open(p, "w", encoding="utf-8", newline=""); wr.write(t); wr.close()
print("5. setting UI OK")
