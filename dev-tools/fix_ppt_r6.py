import io, os, re

os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

# ========== A. IdtPlug-in.cpp ==========
p = "IdtPlug-in.cpp"
t = io.open(p, encoding="utf-8", newline="").read()

# A1. 左侧控件药丸宽度 195 -> 185（内容已左移，收掉尾部空位）
a = "pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_LeftPageWidget].Width.v = (195) * pptComSetlist.bottomSideBothWidgetScale;"
assert a in t, "左药丸宽度"
t = t.replace(a, "pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_LeftPageWidget].Width.v = (185) * pptComSetlist.bottomSideBothWidgetScale;")

# A2. 右侧控件药丸宽度 195 -> 185（黑条在右端，删除后对称收紧）
a = "pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_RightPageWidget].Width.v = (195) * pptComSetlist.bottomSideBothWidgetScale;"
assert a in t, "右药丸宽度"
t = t.replace(a, "pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_RightPageWidget].Width.v = (185) * pptComSetlist.bottomSideBothWidgetScale;")

# A3. 中间 tab 内容 X 基准：SeekBar.X1 + 7 -> tab.X + 10（收掉左侧 15px 空白并居中）
n = t.count("pptUiLineWidgetTarget[PptUiLineWidgetID::BottomSide_MiddleWidget_SeekBar].X1.v + (2 + 5) * pptComSetlist.bottomSideMiddleWidgetScale")
assert n >= 2, n
t = t.replace("pptUiLineWidgetTarget[PptUiLineWidgetID::BottomSide_MiddleWidget_SeekBar].X1.v + (2 + 5) * pptComSetlist.bottomSideMiddleWidgetScale",
              "pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_MiddleTabSlideWidget].X.v + (10) * pptComSetlist.bottomSideMiddleWidgetScale")
print("A. 药丸收紧 + 中间tab内容左移:", n, "处")

io.open(p, "w", encoding="utf-8", newline="").write(t)

# ========== B. IdtFloating.cpp：右键橡皮改为模式无关单一入口 ==========
p = "IdtFloating.cpp"
t = io.open(p, encoding="utf-8", newline="").read()

# B1. 移除之前插在两条 RightClickClose 路径前的处理块
handler = """					// 右键橡皮：清空画布并切回批注模式
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
n = t.count(handler)
assert n == 2, n
t = t.replace(handler, """					if (m.message == WM_RBUTTONDOWN && setlist.RightClickClose)
					{""")
print("B1. 移除旧插入:", n, "处")

# B2. 主取消息点后插入模式无关的右键橡皮处理
a = """	while (!offSignal)
	{
		hiex::getmessage_win32(&m, EM_MOUSE, floating_window);
"""
b = """	while (!offSignal)
	{
		hiex::getmessage_win32(&m, EM_MOUSE, floating_window);

		// 右键橡皮：清空画布并切回批注模式（模式无关，任何状态下生效）
		if (m.message == WM_RBUTTONDOWN && setlist.eraserQuickClean && IsInRect(m.x, m.y, { 192 + 8, floating_windows.height - 156 + 8, 192 + 8 + 80, floating_windows.height - 156 + 8 + 80 }))
		{
			ChangeStateModeToSelection();
			for (int i = 0; i < 20 && stateMode.StateModeSelectEcho != StateModeSelectEnum::IdtSelection; i++) std::this_thread::sleep_for(std::chrono::milliseconds(10));
			ChangeStateModeToPen();

			hiex::flushmessage_win32(EM_MOUSE, floating_window);
		}
"""
assert a in t, "主取消息点未找到"
t = t.replace(a, b)
print("B2. 右键处理移至主循环 OK")

io.open(p, "w", encoding="utf-8", newline="").write(t)
