import io, os

os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")
p = "IdtFloating.cpp"
t = io.open(p, encoding="utf-8", newline="").read()

# 1) 双击计时变量（与 brush_connect 同级声明）
old_decl = "\tint brush_connect = -1;"
new_decl = "\tint brush_connect = -1;\n\tstd::chrono::steady_clock::time_point lastEraserClickTime{};"
assert t.count(old_decl) == 1
t = t.replace(old_decl, new_decl)

# 2) 橡皮左键释放：双击检测
old_click = """								if (!m.lbutton)
								{
									state = 1;
									if (stateMode.StateModeSelect != StateModeSelectEnum::IdtEraser) ChangeStateModeToEraser();

									break;
								}"""
new_click = """								if (!m.lbutton)
								{
									state = 1;

									auto now = std::chrono::steady_clock::now();
									bool doubleClick = (std::chrono::duration_cast<std::chrono::milliseconds>(now - lastEraserClickTime).count() < 400);
									lastEraserClickTime = now;

									if (doubleClick)
									{
										// 双击橡皮：清空画布并切回批注模式
										ChangeStateModeToSelection();
										for (int i = 0; i < 20 && stateMode.StateModeSelectEcho != StateModeSelectEnum::IdtSelection; i++) std::this_thread::sleep_for(std::chrono::milliseconds(10));
										ChangeStateModeToPen();
									}
									else if (stateMode.StateModeSelect != StateModeSelectEnum::IdtEraser) ChangeStateModeToEraser();

									break;
								}"""
assert t.count(old_click) == 1
t = t.replace(old_click, new_click)

# 3) 右键橡皮：清空并切回批注（优先于右键关闭）
old_rc = """					if (m.message == WM_RBUTTONDOWN && setlist.RightClickClose)
					{"""
new_rc = """					// 右键橡皮：清空画布并切回批注模式
					if (m.message == WM_RBUTTONDOWN && IsInRect(m.x, m.y, { 192 + 8, floating_windows.height - 156 + 8, 192 + 8 + 80, floating_windows.height - 156 + 8 + 80 }))
					{
						ChangeStateModeToSelection();
						for (int i = 0; i < 20 && stateMode.StateModeSelectEcho != StateModeSelectEnum::IdtSelection; i++) std::this_thread::sleep_for(std::chrono::milliseconds(10));
						ChangeStateModeToPen();

						hiex::flushmessage_win32(EM_MOUSE, floating_window);

						MouseInteractionManipulated = std::chrono::high_resolution_clock::now();
					}
					else if (m.message == WM_RBUTTONDOWN && setlist.RightClickClose)
					{"""
assert t.count(old_rc) == 1
t = t.replace(old_rc, new_rc)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("橡皮双击/右键交互完成")
