import io, os, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtSetting.cpp"
raw = io.open(p, "rb").read()
lf = "\r\n" if raw.count(b"\r\n") > 100 else "\n"
ls = raw.decode("utf-8").split(lf)
print("初始:", len(ls), "行")

def show(i, ctx=2):
    for j in range(max(0, i-ctx), min(i+ctx+1, len(ls))):
        print("  ", j+1, repr(ls[j][:90]))

# ===== 1. 社区名片块（按行号）=====
i = next(i for i, ln in enumerate(ls) if "// 社区名片" in ln and "0xe716" not in ln)
print("DEBUG:", repr(ls[i][:40]), repr(ls[i+1][:40])); assert ls[i+1].strip() == "{"
# 配平
depth = 0; seen = False; end = None
for j in range(i+1, len(ls)):
    d = 0; ins = False; k = 0
    ln = ls[j]
    while k < len(ln):
        c = ln[k]
        if ins:
            if c == "\\": k += 2; continue
            if c == '"': ins = False
        else:
            if c == '"': ins = True
            elif ln[k:k+2] == "//": break
            elif c == "{": d += 1
            elif c == "}": d -= 1
        k += 1
    depth += d
    if "{" in ln: seen = True
    if seen and depth == 0: end = j; break
print("社区名片块:", i+1, "-", end+1)
assert end - i < 25, "社区名片块异常"
del ls[i:end+1]
print("删除后:", len(ls), "行")

# ===== 2. 字体 zh-TW 块 =====
i = next((i for i, ln in enumerate(ls) if 'I18n::identifying == L"zh-TW"' in ln and i < 900), None)
if i is not None:
    show(i, 2)
    # 若是 if() { ... } 形式
    if i + 1 < len(ls) and ls[i+1].strip() == "{":
        depth = 0; seen = False; end = None
        for j in range(i+1, len(ls)):
            s = ls[j]
            d = s.count("{") - s.count("}")
            depth += d
            if "{" in s: seen = True
            if seen and depth == 0: end = j; break
        print("字体zh-TW块:", i+1, "-", end+1)
        assert end - i < 15
        del ls[i:end+1]
    else:
        # 单行 if（无块）
        del ls[i]
    print("字体清理后:", len(ls), "行")

# ===== 3. QQ群 I18n 分支 =====
i = next((i for i, ln in enumerate(ls) if "I18n::identifying" in ln and "qm.qq.com" in ln), None)
if i is not None:
    indent = ls[i][:len(ls[i]) - len(ls[i].lstrip())]
    content = ls[i].strip().replace('if (I18n::identifying == L"zh-CN") ', "")
    ls[i] = indent + content
    if i + 1 < len(ls) and ls[i+1].strip().startswith("else "):
        del ls[i+1]
    print("QQ群分支清理 OK")

# ===== 4. 主题 combo + 马年迎新卡片 =====
i = next((i for i, ln in enumerate(ls) if '"马年迎新"' in ln), None)
if i is not None:
    # 用 BeginChild("主题" 定位块
    b = next(j for j, ln in enumerate(ls) if 'BeginChild("主题"' in ln)
    s = b
    while s > 0 and ls[s].strip() != "{":
        s -= 1
    print("主题卡片块首:", s+1, repr(ls[s][:60]))
    assert b - s < 12, "主题块首过远"
    depth = 0; seen = False; end = None
    for j in range(s, len(ls)):
        depth += ls[j].count("{") - ls[j].count("}")
        if "{" in ls[j]: seen = True
        if seen and depth == 0: end = j; break
    print("主题卡片块:", s+1, "-", end+1, f"({end-s+1}行)")
    assert end - s < 120, "主题卡片块过大"
    del ls[s:end+1]
    print("删除后:", len(ls), "行")

# ===== 5. 其他单行清理 =====
out = []
removed = 0
for ln in ls:
    if "SetSkinMode" in ln or "setlist.SkinMode" in ln:
        removed += 1
        continue
    if "I18n::" in ln and not ln.strip().startswith("//"):
        removed += 1
        continue
    out.append(ln)
ls = out
print("单行清理:", removed)

# ===== 6. 赞助文案 =====
t = lf.join(ls)
t = t.replace("成功赞助后，可以联系作者将您的昵称和赞助的金额添加到社区名片中以表示感谢。",
              "成功赞助后，可以联系作者（admin@yfyw.top）表示感谢，您的支持将帮助我们持续改进。")

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("完成:", t.count(lf), "行")
print("残余: I18n=", t.count("I18n::"), "SkinMode=", t.count("SkinMode"),
      "SetSkinMode=", t.count("SetSkinMode"), "马年=", t.count("马年迎新"), "社区名片=", t.count("社区名片"))
