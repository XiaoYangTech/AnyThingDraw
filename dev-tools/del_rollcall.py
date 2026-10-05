import io, os, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtSetting.cpp"
raw = io.open(p, "rb").read()
lf = "\r\n" if raw.count(b"\r\n") > 100 else "\n"
ls = raw.decode("utf-8").split(lf)
print("初始:", len(ls), "行")

# 1. 点名器+ClassIsland 区（8542-9036, 1-based）删除
i_start = 8541  # 0-based 8542
i_end = 9035    # 0-based 9036
assert ls[i_start].rstrip() == "{", repr(ls[i_start][:50])
assert ls[i_end].rstrip() == "}", repr(ls[i_end][:50])
assert "BeginChild(\"组件#4\"" in "\n".join(ls[i_start:i_start+10])
assert "组件#5" in "\n".join(ls[i_end-30:i_end]) or "ClassIsland" in "\n".join(ls[i_end-30:i_end])
del ls[i_start:i_end+1]
print("点名器区删除 8542-9036, 现有", len(ls), "行")

# 2. EraserQuickClean 快照
t = lf.join(ls)
a = "\t\tbool SmoothWriting = setlist.smoothWriting;"
assert a in t
if "bool EraserQuickClean" not in t:
    t = t.replace(a, a + "\n\t\tbool EraserQuickClean = setlist.eraserQuickClean;")
    print("EraserQuickClean 快照 OK")

# 3. 残留 智绘教 检查
n = t.count("智绘教")
print("智绘教残留:", n)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("写入:", t.count(lf), "行")
