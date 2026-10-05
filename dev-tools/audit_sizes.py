import io, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

raw = io.open("IdtSetting.cpp", "rb").read()
t = raw.decode("utf-8").replace("\r\n", "\n")
ls = t.split("\n")

pat = re.compile(r'ImGui::BeginChild\("([^"]+)", \{ ([0-9.]+)f \* settingGlobalScale,\s*([0-9.]+)f \* settingGlobalScale \}')
marks = []
for i, ln in enumerate(ls):
    m = pat.search(ln)
    if m:
        marks.append((i, m.group(1), float(m.group(2)), float(m.group(3))))

# 对每个高度 >= 90 的容器，找其后紧随的嵌套 BeginChild（卡片级），统计直接子卡片高度和
print(f"{'行':>6} {'名称':<26} {'容器高':>6} {'内容估':>6} {'余量':>5}")
for idx, (i, name, w, h) in enumerate(marks):
    if h < 90:
        continue
    # 直接子卡片：在下一个同级/更低缩进容器前，收集比当前深度更深的 BeginChild
    base_indent = len(ls[i]) - len(ls[i].lstrip())
    kids = []
    j = i + 1
    while j < len(ls):
        m2 = pat.search(ls[j])
        if m2:
            ind2 = len(ls[j]) - len(ls[j].lstrip())
            if ind2 <= base_indent:
                break
            kids.append(float(m2.group(3)))
        j += 1
    if not kids:
        continue
    content = sum(kids) + 10 * (len(kids) - 1) + 30  # 卡片和+间距+标题
    slack = h - content
    if abs(slack) >= 35:
        print(f"{i+1:>6} {name[:26]:<26} {h:>6.0f} {content:>6.0f} {slack:>+5.0f}")
