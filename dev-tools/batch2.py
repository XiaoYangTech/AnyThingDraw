import io, os, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtSetting.cpp"
raw = io.open(p, "rb").read()
lf = "\r\n" if raw.count(b"\r\n") > 100 else "\n"
ls = raw.decode("utf-8").split(lf)
print("初始:", len(ls), "行")

# ===== a. 提取配置清理卡片（行 1637-1705 → index 1636-1704）=====
card = ls[1636:1705]
assert "启用配置清理" in "\n".join(card)
assert card[0].strip() == "{", repr(card[0])
assert card[-1].strip() == "}", repr(card[-1])
print("卡片:", len(card), "行")

# ===== b. 插入到软件版本#4（架构卡结束后，行 2445 `}` 之后 → index 2445）=====
ins = 2445
assert ls[ins - 1].strip() == "}", repr(ls[ins - 1][:50])
assert "目标更新架构" in "\n".join(ls[ins - 200:ins])
ls[ins:ins] = card
print("插入 OK，现在", len(ls), "行")

# ===== c. 删除 case tabConfiguration（行 1608-1726 → index 1607-1725）=====
assert "// 配置保存" in ls[1607], repr(ls[1607])
assert "case settingTabEnum::tabConfiguration:" in ls[1608]
assert ls[1725].strip() == "}", repr(ls[1725])
assert "break;" in ls[1724]
del ls[1607:1726]
print("case 删除 OK，现在", len(ls), "行")

# ===== d. 删除导航按钮（行 1020-1045 → index 1019-1044）=====
assert "// 软件配置" in ls[1019], repr(ls[1019])
assert "tabConfiguration" in ls[1024]
assert ls[1044].strip() == "}", repr(ls[1044][:50])
del ls[1019:1045]
print("导航删除 OK，现在", len(ls), "行")

# ===== e. 删除 enum 成员 =====
i = next(i for i, ln in enumerate(ls) if ln.strip() == "tabConfiguration,")
del ls[i]
print("enum 删除 OK")

# ===== f. 软件版本#4 高度 180 → 300 =====
t = lf.join(ls)
a = 'ImGui::BeginChild("软件版本#4", { 750.0f * settingGlobalScale,180.0f * settingGlobalScale }, false, ImGuiWindowFlags_NoScrollbar | ImGuiWindowFlags_NoScrollWithMouse);'
assert a in t
t = t.replace(a, a.replace("180.0f", "300.0f"))
print("高度 300 OK")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("写入:", t.count(lf), "行")
