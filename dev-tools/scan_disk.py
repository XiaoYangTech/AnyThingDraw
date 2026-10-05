import sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MARKER = "双击或右键橡皮快速清空并切回批注".encode("utf-8")
MARKER2 = "点击中间页码打开大纲视图".encode("utf-8")
TARGET_SIZE = 401408  # 截断前文件大小

raw = open(r"\\.\D:", "rb", buffering=0)
import msvcrt
raw_handle = msvcrt.get_osfhandle(raw.fileno())

# D盘总扇区
import ctypes
kernel32 = ctypes.windll.kernel32
# 用 GetDiskFreeSpace 获取扇区/簇参数
sectors_per_cluster = ctypes.c_ulonglong()
bytes_per_sector = ctypes.c_ulonglong()
free_clusters = ctypes.c_ulonglong()
total_clusters = ctypes.c_ulonglong()
root = ctypes.c_wchar_p("D:\\")
kernel32.GetDiskFreeSpaceW(root, ctypes.byref(sectors_per_cluster), ctypes.byref(bytes_per_sector),
                           ctypes.byref(free_clusters), ctypes.byref(total_clusters))
bps = bytes_per_sector.value
spc = sectors_per_cluster.value
total_bytes = total_clusters.value * spc * bps
print(f"扇区 {bps}B, 簇 {spc}扇区, 总容量 {total_bytes/2**30:.0f} GiB")

CHUNK = 4 * 1024 * 1024
found_at = None
overlap = 64
pos = 0
tail = b""
read_size = ctypes.c_ulonglong()
buf = ctypes.create_string_buffer(CHUNK)

# 从后往前扫描更快？文件写在 14:31（今天），NTFS 通常向后分配。先试前 30% 也行——直接顺序扫，找到即停。
# 实际上：直接从头顺序扫，速度 ~200MB/s，144GB ≈ 12分钟。加进度输出。
import time
t0 = time.time()
while pos < total_bytes:
    kernel32.ReadFile(raw_handle, buf, CHUNK, ctypes.byref(read_size), None)
    n = read_size.value
    if n == 0:
        break
    data = tail + buf.raw[:n]
    if MARKER in data:
        found_at = pos - len(tail) + data.find(MARKER)
        print(f"找到标记于原始偏移 {found_at} ({found_at/2**30:.2f} GiB)")
        break
    tail = data[-overlap:]
    pos += n
    if (pos // (1024**3)) != ((pos - n) // (1024**3)):
        el = time.time() - t0
        print(f"  已扫 {pos/2**30:.0f} GiB, {el:.0f}s", flush=True)

if found_at is None:
    print("未找到标记")
    sys.exit(1)

# 回读包含整个文件的窗口：文件 401KB，标记在文件内约 2/3 处（5420/8120 行 ≈ 字节 66%）
# 提取 [found - 280KB, found + 140KB] 再精确裁剪
AL = 512
win_start = (max(0, found_at - 280 * 1024) // AL) * AL
win_size = ((TARGET_SIZE + 64 * 1024 + AL - 1) // AL) * AL
kernel32.SetFilePointer(raw_handle, ctypes.c_long(win_start & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(win_start >> 32)), 0)
kernel32.ReadFile(raw_handle, buf, win_size, ctypes.byref(read_size), None)
window = buf.raw[:read_size.value]
m2 = window.find(MARKER)
assert m2 >= 0, "窗口内未找到标记"
abs_marker = win_start + m2

# 文件起点：从标记向前找文件头特征（IdtSetting.cpp 开头是 BOM 或 #include / #pragma）
head_marker = b'ImFontMain->Scale = 0.8f, PushFontNum++, ImGui::PushFont(ImFontMain);'
# 更稳：向前找 "IMGUI_CHECKVERSION();"（文件唯一）——它在文件开头 550 行附近
head_m = b'IMGUI_CHECKVERSION();'
# 文件头在标记前 ~66% 处
guess_head = abs_marker - int(TARGET_SIZE * 0.62)
scan_from = max(0, guess_head - 64 * 1024)
kernel32.SetFilePointer(raw_handle, ctypes.c_long(scan_from & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(scan_from >> 32)), 0)
kernel32.ReadFile(raw_handle, buf, 512 * 1024, ctypes.byref(read_size), None)
region = buf.raw[:read_size.value]
hi = region.find(head_m)
assert hi >= 0, "未找到文件头标记"
file_start_abs = scan_from + hi
# 精确文件开头：从 head_m 向前找该"函数/文件"的真实起始——head_m 前最近的 BOM 或行首 `#`
# IdtSetting.cpp 的第一行（经检查）是中文注释或 #include；找 UTF-8 BOM 优先
back = region.rfind(b"\xef\xbb\xbf", 0, hi)
if back >= 0 and hi - back < 200 * 1024:
    file_start_rel = back
else:
    # 找 head_m 前第一个行首 '#'
    file_start_rel = region.rfind(b"\n#", 0, hi) + 1
file_start_abs = scan_from + file_start_rel

# 文件尾：从标记向后 401KB 窗口找文件尾特征（文件最后内容 + 之后是其他数据）
kernel32.SetFilePointer(raw_handle, ctypes.c_long(abs_marker & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(abs_marker >> 32)), 0)
kernel32.ReadFile(raw_handle, buf, TARGET_SIZE + 256 * 1024, ctypes.byref(read_size), None)
tail_data = buf.raw[:read_size.value]
# 文件最后一行（截断版 shell 尾）："                        ImGui::EndChild();\n..."？不对——完整版尾：
# IdtSetting.cpp 8120 行版的最后 20 行与其他文件相同模式：函数收尾 + 全局数据。找 "LPDIRECT3D9 g_pD3D"
tail_m = tail_data.find(b"LPDIRECT3D9 g_pD3D")
assert tail_m >= 0, "未找到文件尾标记"
file_end_rel = tail_m + len(b"LPDIRECT3D9 g_pD3D = nullptr;")
# 向后补齐到该行行尾（找 \n）
while tail_data[file_end_rel:file_end_rel+1] != b"\n":
    file_end_rel += 1
file_len = file_end_rel - file_start_rel + 0
# 重新以精确窗口提取
kernel32.SetFilePointer(raw_handle, ctypes.c_long(file_start_abs & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(file_start_abs >> 32)), 0)
kernel32.ReadFile(raw_handle, buf, file_len + 4096, ctypes.byref(read_size), None)
content = buf.raw[:file_len]

out = os.path.join(os.getcwd(), "IdtSetting_recovered.cpp")
with open(out, "wb") as f:
    f.write(content)
print(f"恢复 {len(content)} 字节 -> {out}")
print("行数:", content.count(b"\n"))
print("标记验证:", MARKER in content, MARKER2 in content)
raw.close()
