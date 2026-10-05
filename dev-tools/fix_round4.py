import io, os

os.chdir(r"D:\开发\AnythingDraw\Inkeys\AnyThingDraw")

# 1. IdtSetting.cpp：版本显示简化 + 工具栏文字
p = "IdtSetting.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
a = 'text += L"\\n软件发布版本 " + (editionDate.length() >= 8 ? editionDate.substr(0, 4) + L"年" + editionDate.substr(4, 2) + L"月" + editionDate.substr(6, 2) + L"日" : editionDate) + L"（" + editionChannel + L"）";'
b = 'text += L"\\n软件发布版本 " + editionDate + L"（" + editionChannel + L"）";'
assert a in t, "version line not found"
t = t.replace(a, b)
for old, new in [
    ('graphics.DrawString(L"选择(清空)"', 'graphics.DrawString(L"选择并清空"'),
    ('graphics.DrawString(L"画笔"', 'graphics.DrawString(L"批注"'),
    ('graphics.DrawString(L"选项"', 'graphics.DrawString(L"设置"'),
    ('graphics.DrawString(L"定格"', 'graphics.DrawString(L"冻屏"'),
    ('graphics.DrawString(L"穿透"', 'graphics.DrawString(L"鼠标"'),
]:
    n = t.count(old)
    assert n > 0, old
    t = t.replace(old, new)
    print(old[22:34], "->", n, "处")
io.open(p, "w", encoding="utf-8", newline="").write(t)

# 2. IdtMain.cpp：版本号 1.0.0
p = "IdtMain.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
assert 'L"20260713a"' in t
t = t.replace('wstring editionDate = L"20260713a";', 'wstring editionDate = L"1.0.0";')
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("editionDate -> 1.0.0")

# 3. IdtPlug-in.cpp：快捷方式名
p = "IdtPlug-in.cpp"
t = io.open(p, encoding="utf-8", newline="").read()
n = t.count("亿方万能画笔(屏幕批注工具)")
t = t.replace("亿方万能画笔(屏幕批注工具)", "亿方万能画笔")
io.open(p, "w", encoding="utf-8", newline="").write(t)
print("IdtPlug-in.cpp lnk:", n)
