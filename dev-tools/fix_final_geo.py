import io, os, re

os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtPlug-in.cpp"
t = io.open(p, encoding="utf-8", newline="").read()

def sub1(a, b, tag):
    global t
    assert t.count(a) == 1, f"{tag}: count={t.count(a)}"
    t = t.replace(a, b)

for side in ["Left", "Right"]:
    sc = "bottomSideBothWidgetScale"
    outer = f"BottomSide_{side}PageWidget"
    # 1) prev/next 按钮回原始几何：X/Y 补回 +5 偏移
    for btn in ["PreviousPage", "NextPage"]:
        a = f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].X.v = pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}].X.v;"
        sub1(a, f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].X.v = pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}].X.v + (5) * pptComSetlist.{sc};", f"{side} {btn} X")
        a = f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].Y.v = pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}].Y.v;"
        sub1(a, f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].Y.v = pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}].Y.v + (5) * pptComSetlist.{sc};", f"{side} {btn} Y")
        # 2) 高度 60 -> 50（铺满回退）
        a = f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].Height.v = (60) * pptComSetlist.{sc};"
        sub1(a, f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].Height.v = (50) * pptComSetlist.{sc};", f"{side} {btn} H")
        # 3) 椭圆 30 -> 35（半径 17.5，原版圆润度）
        for dim in ["EllipseWidth", "EllipseHeight"]:
            a = f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].{dim}.v = (30) * pptComSetlist.{sc};"
            sub1(a, f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].{dim}.v = (35) * pptComSetlist.{sc};", f"{side} {btn} {dim}")
    # 4) 图标 Y +10 -> +5
    for btn in ["PreviousPage", "NextPage"]:
        icon = f"BottomSide_{side}{'Previous' if btn == 'PreviousPage' else 'Next'}Page"
        a = f"pptUiImageWidgetTarget[PptUiImageWidgetID::{icon}].Y.v = pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].Y.v + (10) * pptComSetlist.{sc};"
        sub1(a, f"pptUiImageWidgetTarget[PptUiImageWidgetID::{icon}].Y.v = pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_{btn}].Y.v + (5) * pptComSetlist.{sc};", f"{side} icon Y")
    # 5) next.X 恢复原公式（页码右侧 +5，自动落在 +130..180，药丸 185 内）
    words = f"BottomSide_{side}PageNum_Above"
    a = f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_NextPage].X.v = pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}].X.v + (145) * pptComSetlist.{sc};"
    sub1(a, f"pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::{outer}_NextPage].X.v = pptUiWordsWidgetTarget[PptUiWordsWidgetID::{words}].Right.v + (5) * pptComSetlist.{sc};", f"{side} next formula")

# 6) 右药丸锚点：宽度 185 后右缘对齐（200 -> 190）
sub1("floor(PPTMainMonitor.MonitorWidth - pptComSetlist.bottomBothWidth - (200) * pptComSetlist.bottomSideBothWidgetScale);",
     "floor(PPTMainMonitor.MonitorWidth - pptComSetlist.bottomBothWidth - (190) * pptComSetlist.bottomSideBothWidgetScale);", "右药丸锚点")

# 7) 中间 tab 收窄 70 -> 60，按钮贴 +5
sub1("pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_MiddleTabSlideWidget].Width.v = (70) * pptComSetlist.bottomSideMiddleWidgetScale;",
     "pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_MiddleTabSlideWidget].Width.v = (60) * pptComSetlist.bottomSideMiddleWidgetScale;", "中间tab宽")
sub1("floor(PPTMainMonitor.MonitorWidth / 2 + pptComSetlist.bottomMiddleWidth + (-70 / 2.0f) * pptComSetlist.bottomSideMiddleWidgetScale);",
     "floor(PPTMainMonitor.MonitorWidth / 2 + pptComSetlist.bottomMiddleWidth + (-60 / 2.0f) * pptComSetlist.bottomSideMiddleWidgetScale);", "中间tab居中")
sub1("pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_MiddleTabSlideWidget_EndShow].X.v = pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_MiddleTabSlideWidget].X.v + (10) * pptComSetlist.bottomSideMiddleWidgetScale;",
     "pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_MiddleTabSlideWidget_EndShow].X.v = pptUiRoundRectWidgetTarget[PptUiRoundRectWidgetID::BottomSide_MiddleTabSlideWidget].X.v + (5) * pptComSetlist.bottomSideMiddleWidgetScale;", "EndShow X")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("IdtPlug-in.cpp 几何修复完成")

# ===== IdtSetting.cpp：绘制行为分组扩高 =====
p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
a = 'ImGui::BeginChild("绘制#3", { 750.0f * settingGlobalScale,90.0f * settingGlobalScale }, false, ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);'
assert t.count(a) == 1
t = t.replace(a, a.replace("90.0f", "160.0f"))
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("绘制#3 分组 90 -> 160 完成")
