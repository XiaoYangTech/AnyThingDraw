import ctypes, os, sys, msvcrt

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MARKER = "双击或右键橡皮快速清空并切回批注".encode("utf-8")
TARGET = 401408
HEADMARK = b"import AnyThingDraw.Thread.Status;"
TAILMARK = b"ImGui::SetScrollY(window, window->Scroll.y + delta.y);\n}"

raw = open(r"\\.\D:", "rb", buffering=0)
raw_handle = msvcrt.get_osfhandle(raw.fileno())
kernel32 = ctypes.windll.kernel32

abs_marker = 36012297
AL = 512

def read_at(off, size):
    a = (off // AL) * AL
    delta = off - a
    sz = ((size + delta + AL - 1) // AL) * AL
    kernel32.SetFilePointer(raw_handle, ctypes.c_long(a & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(a >> 32)), 0)
    buf = ctypes.create_string_buffer(sz)
    got = ctypes.c_ulonglong()
    kernel32.ReadFile(raw_handle, buf, sz, ctypes.byref(got), None)
    return a, buf.raw[:got.value], delta

# 文件头锚点窗口：标记前 401KB
ws, wd, _ = read_at(abs_marker - TARGET, TARGET)
hm = wd.find(HEADMARK)
assert hm >= 0, "文件头锚点未找到（窗口内）"
file_start = ws + hm
print("文件起始:", file_start)

# 读整个文件 + 尾部余量
_, content_buf, _ = read_at(file_start, TARGET + 8192)
content = content_buf[:TARGET]
assert content[:len(HEADMARK)] == HEADMARK, "文件头不匹配"
print("头锚点在偏移0 ✓")
print("尾标记在文件尾:", TAILMARK in content)

out = os.path.join(os.getcwd(), "IdtSetting_recovered.cpp")
with open(out, "wb") as f:
    f.write(content)
print(f"恢复 {len(content)} 字节 -> {out}")
raw.close()
