import io, os, re, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
print("初始行数:", t.count("\n"))

# ===== 1. I18n 相关 =====
# include 移除
t = t.replace('#include "IdtI18n.h"\n', "")
# I18n::load 调用行删除（整个 I18N初始化 块在 IdtMain 里，这里只清理 IdtSetting 的引用）
lines = t.split("\n")
out = []
skip_until_depth_zero = False
depth = 0
for ln in lines:
    if "I18n::load(" in ln and not ln.strip().startswith("//"):
        # 删除该行
        continue
    if "I18n::identifying" in ln and not ln.strip().startswith("//"):
        # 这些行属于 if/else 分支——保留 zh-CN 分支内容
        # 处理模式：识别模式后保留下一行的内容
        # 简化：将识别行替换为空注释，保留后续行
        out.append("// [i18n removed] " + ln.strip()[:40])
        continue
    out.append(ln)
t = "\n".join(out)

# I18n::identifying if/else 分支：找到 else 分支内容并只保留 zh-CN
# Home1 图片加载
lines = t.split("\n")
out = []
i = 0
while i < len(lines):
    ln = lines[i]
    if "I18n::identifying == L\"zh-CN\"" in ln and "idtLoadImage" in ln:
        # 保留这行（zh-CN），删除后面两行 else if / else
        out.append(ln.replace('if (I18n::identifying == L"zh-CN") ', ""))
        if i + 1 < len(lines) and "zh-TW" in lines[i + 1]:
            i += 2  # skip zh-TW and en-US
        elif i + 2 < len(lines) and "zh-TW" in lines[i + 1]:
            i += 2
        i += 1
        continue
    elif "I18n::identifying == L\"zh-CN\"" in ln and "ShellExecuteW" in ln:
        out.append(ln.replace('if (I18n::identifying == L"zh-CN") ', ""))
        if i + 1 < len(lines) and "else" in lines[i + 1]:
            i += 1  # skip else line
        i += 1
        continue
    out.append(ln)
    i += 1
t = "\n".join(out)

# ===== 2. SkinMode =====
# 颜色分支简化
t = t.replace("if (setlist.SkinMode == 1 || setlist.SkinMode == 2)", "if (true)")
# SkinMode==3 分支删除
lines = t.split("\n")
i = 0
while i < len(lines):
    if "else if (setlist.SkinMode == 3)" in lines[i]:
        depth = 0; seen = False; end = None
        for j in range(i, len(lines)):
            depth += lines[j].count("{") - lines[j].count("}")
            if "{" in lines[j]: seen = True
            if seen and depth == 0: end = j; break
        del lines[i:end + 1]
        continue
    i += 1
t = "\n".join(lines)
# 皮肤加载行删除
for a in [
    '\t\t\tidtLoadImage(&skin[1], L"PNG", L"skin1");\n',
    '\t\t\tidtLoadImage(&skin[3], L"PNG", L"skin1-3");\n',
]:
    t = t.replace(a, "")
# bskin3/skin[3] 残余行
lines = t.split("\n")
out = []
for ln in lines:
    if ("skin[3]" in ln or "bskin3" in lines[lines.index(ln) if ln in lines else 0]) and "skin[2]" not in ln:
        continue
    out.append(ln)
t = "\n".join(out)

# ===== 3. showLoadingScreen =====
# 开关卡片删除
lines = t.split("\n")
i = 0
while i < len(lines):
    if 'BeginChild("显示加载页面"' in lines[i]:
        depth = 0; seen = False; end = None
        for j in range(i, len(lines)):
            depth += lines[j].count("{") - lines[j].count("}")
            if "{" in lines[j]: seen = True
            if seen and depth == 0: end = j; break
        del lines[i:end + 1]
        continue
    i += 1
t = "\n".join(lines)
t = t.replace("bool PptComShowLoadingScreen = pptComSetlist.showLoadingScreen;\n", "")
t = t.replace("pptComSetlist.showLoadingScreen = PptComShowLoadingScreen;\n", "")
# IdtPlug-in 的触发已在之前处理

# ===== 4. SetSkinMode/SkinMode 成员和配置 =====
# IdtSetting 里的局部变量和 combo
lines = t.split("\n")
i = 0
while i < len(lines):
    if "SetSkinMode" in lines[i] and "int" in lines[i]:
        del lines[i]
        continue
    i += 1
t = "\n".join(lines)
# 主题 combo 块删除
lines = t.split("\n")
i = 0
while i < len(lines):
    if 'BeginCombo("##主题"' in lines[i]:
        depth = 0; seen = False; end = None
        for j in range(i, len(lines)):
            depth += lines[j].count("{") - lines[j].count("}")
            if "{" in lines[j]: seen = True
            if seen and depth == 0: end = j; break
        if end is not None:
            del lines[i:end + 1]
        continue
    i += 1
t = "\n".join(lines)

# ===== 5. 首启语言检测 =====
lines = t.split("\n")
i = 0
while i < len(lines):
    if "GetUserDefaultUILanguage" in lines[i]:
        # 向上找 {
        k = i
        while k > 0 and lines[k].rstrip() != "{":
            k -= 1
        depth = 0; seen = False; end = None
        for j in range(k, len(lines)):
            depth += lines[j].count("{") - lines[j].count("}")
            if "{" in lines[j]: seen = True
            if seen and depth == 0: end = j; break
        if end is not None:
            del lines[k:end + 1]
        continue
    i += 1
t = "\n".join(lines)

io.open(p, "w", encoding="utf-8", newline="").write(t)
print("清理完成:", t.count("\n"), "行,", len(t), "字节")
print("残余检查: SkinMode=", t.count("SkinMode"), " I18n=", t.count("I18n::"), " showLoadingScreen=", t.count("showLoadingScreen"))
