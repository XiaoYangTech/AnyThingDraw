import ctypes, os, sys, msvcrt

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MARKER = "双击或右键橡皮快速清空并切回批注".encode("utf-8")
TARGET = 401408
HEADMARK = b"IMGUI_CHECKVERSION();"
TAILMARK = b"LPDIRECT3D9 g_pD3D"

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

# 窗口：标记前后各 401KB
win_start, win_data, delta = read_at(abs_marker - TARGET, TARGET * 2 + AL)
m = win_data.find(MARKER)
assert m >= 0
abs_marker = win_start + m
print("标记精确偏移:", abs_marker)

# 窗口：IMGUI_CHECKVERSION 候选（标记前 401KB）
ws, wd, _ = read_at(abs_marker - TARGET, TARGET)
cands = []
pos = 0
while True:
    c = wd.find(HEADMARK, pos)
    if c < 0:
        break
    cands.append(ws + c)
    pos = c + 1
print("IMGUI_CHECKVERSION 候选:", len(cands))

best = None
for c in cands:
    fs = c - 27000  # IMGUI_CHECKVERSION 在文件 ~6.8% 处
    if fs < 0:
        continue
    # 读取 [fs, fs+TARGET] 验证尾部标记
    _, d2, d2o = read_at(fs, TARGET)
    tail = d2.find(TAILMARK)
    if tail >= 0 and TARGET - tail < 2048:  # 尾标记接近文件尾
        best = fs
        print("候选通过:", fs, "尾标记距文件尾:", TARGET - tail)
        break

if best is None:
    print("无候选通过，尝试放宽……")
    sys.exit(1)

# 精确头部：从 best 向前找文件真实首字节（前一行边界）
_, d3, _ = read_at(best - 4096, 4096 + 512)
# best 相对窗口偏移
rel = (best % AL) + (4096 // AL) * AL - (4096 // AL) * AL  # best-4096 对齐后 delta=4096-(best%AL)
rel = 4096 - ((best % AL) if (best % AL) else AL) if False else (best - (best - 4096))
# 直接用非对齐读处理头部微调
_, d3, _ = read_at(best - 4096, 4096 + 512)
rel = best - (best - 4096)  # = 4096
# 找 d3 中 head 前最后的换行（文件首行开始）
seg = d3[:512]
nl = seg.rfind(b"\n", 0, 4096 - 27000 + 64)
# 简化：文件头 = IMGUI_CHECKVERSION 行的行首；向前多退一个换行
head_line_start = best - 27000
_, d4, _ = read_at(head_line_start - 256, 512)
# 找 head_line_start 前 256 字节里最后一个 \n
nl = d4.rfind(b"\n")
file_start = head_line_start - 256 + nl + 1

content = read_at(file_start, TARGET)[1]
with open(os.path.join(os.getcwd(), "IdtSetting_recovered.cpp"), "wb") as f:
    f.write(content)
print(f"恢复 {len(content)} 字节 -> IdtSetting_recovered.cpp")
print("尾标记在文件内:", TAILMARK in content)
raw.close()
