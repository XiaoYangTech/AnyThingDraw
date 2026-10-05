import io, os, re

os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

def depth_delta(line):
    d = 0
    in_str = False
    i = 0
    while i < len(line):
        c = line[i]
        if in_str:
            if c == "\\":
                i += 2
                continue
            if c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif line[i:i+2] == "//":
                break
            elif c == "{":
                d += 1
            elif c == "}":
                d -= 1
        i += 1
    return d

def del_block(lines, start, brace_line=None):
    """从 start 行开始删除到与起始深度配平；brace_line 指定配平基准行"""
    base = brace_line if brace_line is not None else start
    depth = 0
    for j in range(base, len(lines)):
        depth += depth_delta(lines[j])
        if j >= start and depth == 0:
            return j
    raise RuntimeError("unbalanced")

# ===== 1. IdtFloating.cpp =====
p = "IdtFloating.cpp"
lines = io.open(p, encoding="utf-8", newline="").read().split("\n")

# 1a. 删除所有 else if (setlist.SkinMode == 3) 块（含 //龙年迎新 等注释行）
removed = 0
i = 0
while i < len(lines):
    ln = lines[i]
    if "else if (setlist.SkinMode == 3)" in ln:
        cstart = i
        while cstart > 0 and lines[cstart - 1].strip().startswith("//"):
            cstart -= 1
        depth = 0
        seen = False
        end = None
        for j in range(i, len(lines)):
            depth += depth_delta(lines[j])
            if "{" in lines[j]:
                seen = True
            if seen and depth == 0:
                end = j
                break
        del lines[cstart:end + 1]
        removed += 1
        continue
    i += 1
print("1a. SkinMode==3 块删除:", removed)

# 1b. 剩余 SkinMode 条件常量化
t = "\n".join(lines)
t = t.replace("(setlist.SkinMode == 1 || setlist.SkinMode == 2)", "(true)")
t = t.replace("setlist.SkinMode == 1", "true")
lines = t.split("\n")

# 1c. 删除 else if (setlist.SkinMode == 2) 块（极简时钟专属，皮肤系统删除后不可达）
removed = 0
i = 0
while i < len(lines):
    if "else if (setlist.SkinMode == 2)" in lines[i]:
        depth = 0
        seen = False
        end = None
        for j in range(i, len(lines)):
            depth += depth_delta(lines[j])
            if "{" in lines[j]:
                seen = True
            if seen and depth == 0:
                end = j
                break
        del lines[i:end + 1]
        removed += 1
        continue
    i += 1
print("1c. SkinMode==2 块删除:", removed)

# 1d. 删除 skin[1]/skin[3]/bskin3 的加载与声明
t = "\n".join(lines)
for a in [
    '\t\t\tidtLoadImage(&skin[1], L"PNG", L"skin1");\n',
    '\t\t\tidtLoadImage(&skin[3], L"PNG", L"skin1-3");\n',
    "\t\t\tbskin3 = IMAGEToBitmap(&skin[3]);\n",
    "\tBitmap* bskin3;\n",
]:
    if a in t:
        t = t.replace(a, "")
        print("已删:", a.strip()[:50])
lines = t.split("\n")

# 1e. 删除 skin[3]/bskin3 的残余引用行（若仍有）
i = 0
while i < len(lines):
    if ("skin[3]" in lines[i] or "bskin3" in lines[i]) and "skin[2]" not in lines[i]:
        del lines[i]
        print("删残留行:", i + 1)
        continue
    i += 1
io.open(p, "w", encoding="utf-8", newline="").write("\n".join(lines))

# ===== 2. IdtSetting.cpp：主题选择卡片删除 + SkinMode 引用清理 =====
p = "IdtSetting.cpp"
lines = io.open(p, encoding="utf-8", newline="").read().split("\n")
# 找 主题 combo 所在卡片块（从 SetSkinMode 局部声明回溯到包裹 {）
idx = next(i for i, ln in enumerate(lines) if "int SetSkinMode = setlist.SetSkinMode;" in ln)
s = idx
while s > 0 and lines[s].rstrip() != "\t\t\t\t\t{":
    s -= 1
depth = 0
end = None
for j in range(s, len(lines)):
    depth += depth_delta(lines[j])
    if j > s and depth == 0:
        end = j
        break
del lines[s:end + 1]
print("2. 主题卡片删除:", s + 1, "-", end + 1)
t = "\n".join(lines)
t = t.replace("setlist.SetSkinMode", "0")  # 兜底（应已无）
io.open(p, "w", encoding="utf-8", newline="").write(t)

# ===== 3. IdtMain.cpp / IdtConfiguration：成员与默认值 =====
p = "IdtMain.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
for a in [
    "\t\t\t\tsetlist.SetSkinMode = 0;\n",
    "\t\t\t\tsetlist.SkinMode = 1;\n",
]:
    if a in t:
        t = t.replace(a, "")
io.open(p, "w", encoding="utf-8", newline="").write(t)

p = "IdtConfiguration.h"
t = io.open(p, encoding="utf-8", newline="").read()
for a in ["\tint SetSkinMode, SkinMode;\n"]:
    if a in t:
        t = t.replace(a, "")
io.open(p, "w", encoding="utf-8", newline="").write(t)

p = "IdtConfiguration.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
for a in [
    '\t\tif (updateVal.isMember("SetSkinMode") && updateVal["SetSkinMode"].isInt())\n\t\t\tsetlist.SetSkinMode = updateVal["SetSkinMode"].asInt();\n',
    '\t\tif (updateVal.isMember("SkinMode") && updateVal["SkinMode"].isInt())\n\t\t\tsetlist.SkinMode = updateVal["SkinMode"].asInt();\n',
    '\t\tupdateVal["SetSkinMode"] = Json::Value(setlist.SetSkinMode);\n',
    '\t\tupdateVal["SkinMode"] = Json::Value(setlist.SkinMode);\n',
]:
    if a in t:
        t = t.replace(a, "")
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("3. SkinMode 成员/IO/默认值清理完成")

# ===== 4. 加载页面（showLoadingScreen）删除 =====
# 4a. IdtSetting.cpp：开关卡片删除
p = "IdtSetting.cpp"
lines = io.open(p, encoding="utf-8", newline="").read().split("\n")
idx = next(i for i, ln in enumerate(lines) if "bool PptComShowLoadingScreen = pptComSetlist.showLoadingScreen;" in ln)
s = idx
while s > 0 and lines[s].rstrip() != "\t\tbool PptComShowLoadingScreen = pptComSetlist.showLoadingScreen;":
    s -= 1
# 找 显示加载页面 卡片块
idx2 = next(i for i, ln in enumerate(lines) if 'BeginChild("显示加载页面"' in ln)
s2 = idx2
while s2 > 0 and lines[s2].rstrip() != "\t\t\t\t\t\t{":
    s2 -= 1
depth = 0
end2 = None
for j in range(s2, len(lines)):
    depth += depth_delta(lines[j])
    if j > s2 and depth == 0:
        end2 = j
        break
del lines[s2:end2 + 1]
t = "\n".join(lines)
a = "\t\tbool PptComShowLoadingScreen = pptComSetlist.showLoadingScreen;\n"
t = t.replace(a, "")
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("4a. 加载页面开关卡片删除")

# 4b. IdtConfiguration：成员与读写
p = "IdtConfiguration.h"
t = io.open(p, encoding="utf-8", newline="").read()
t = t.replace("\t\tshowLoadingScreen = false;\n", "")
t = t.replace("\tbool showLoadingScreen;\n", "")
io.open(p, "w", encoding="utf-8", newline="").write(t)
p = "IdtConfiguration.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
a = '\t\tif (updateVal.isMember("ShowLoadingScreen") && updateVal["ShowLoadingScreen"].isBool())\n\t\t\tpptComSetlist.showLoadingScreen = updateVal["ShowLoadingScreen"].asBool();\n'
assert a in t
t = t.replace(a, "")
a = '\t\tupdateVal["ShowLoadingScreen"] = Json::Value(pptComSetlist.showLoadingScreen);\n'
assert a in t
t = t.replace(a, "")
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("4b. showLoadingScreen 配置删除")

# 4c. IdtPlug-in.cpp：触发行删除
p = "IdtPlug-in.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
a = "if (!ppt_title_recond[ppt_title] && pptComSetlist.showLoadingScreen) FreezePPT = true;\n"
assert a in t
t = t.replace("\t\t\t" + a, "")
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("4c. FreezePPT 触发删除")
