import ctypes, msvcrt, sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# IdtSetting.cpp 独有内容（脚本文件中不含）
NEEDLE = "同类软件悬浮窗拦截助手(DesktopDrawpadBlocker)是依据 GPLv3 许可协议发布的开源软件".encode("utf-8")
ERASER = "双击或右键橡皮快速清空并切回批注".encode("utf-8")
TARGET = 401408

raw = open(r"\\.\D:", "rb", buffering=0)
h = msvcrt.get_osfhandle(raw.fileno())
k = ctypes.windll.kernel32
AL = 512
CHUNK = 8 * 1024 * 1024

total_bytes = 144 * 1024 * 1024 * 1024
buf = ctypes.create_string_buffer(CHUNK + 4096)
got = ctypes.c_ulonglong()
pos = 0
tail = b""
hits = []
t0 = time.time()

while pos < total_bytes:
    k.ReadFile(h, buf, CHUNK, ctypes.byref(got), None)
    n = got.value
    if n == 0:
        break
    data = tail + buf.raw[:n]
    start = 0
    while True:
        m = data.find(NEEDLE, start)
        if m < 0:
            break
        hits.append(pos - len(tail) + m)
        start = m + 1
    tail = data[-(len(NEEDLE) + 64):]
    pos += n
    el = time.time() - t0
    if int(el) % 60 == 0 and int(el) > 0:
        gb = pos / 2**30
        print(f"  {gb:.0f} GiB, {el:.0f}s, hits={len(hits)}", flush=True)
    if pos >= total_bytes:
        break

print(f"扫描完成 {pos/2**30:.0f} GiB, 用时 {time.time()-t0:.0f}s, DDB串命中: {hits}")
raw.close()

if not hits:
    print("全盘未找到 IdtSetting.cpp 内容")
    sys.exit(1)

# 取第一个命中，计算文件起点并提取验证
import msvcrt
raw = open(r"\\.\D:", "rb", buffering=0)
h = msvcrt.get_osfhandle(raw.fileno())
k = ctypes.windll.kernel32

for hit in hits[:4]:
    guess_start = hit - int(0.74 * TARGET)
    ALR = 512
    ra = (guess_start // ALR) * ALR
    k.SetFilePointer(h, ctypes.c_long(ra & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(ra >> 32)), 0)
    big = ctypes.create_string_buffer(TARGET + 2 * ALR)
    got2 = ctypes.c_ulonglong()
    k.ReadFile(h, big, len(big), ctypes.byref(got2), None)
    d = big.raw[:got2.value]
    rel = d.find(NEEDLE)
    if rel < 0:
        continue
    # 精确文件起点：DDB串前面找 import 行
    imp = d.rfind(b"import AnyThingDraw.Thread.Status;", 0, rel)
    if imp < 0:
        print(f"hit@{hit}: import 未找到")
        continue
    fs = ra + imp
    content = d[imp:imp + TARGET]
    print(f"hit@{hit}: import@{fs}, 头匹配={content[:20] == b'import AnyThingDraw.'}, 尾标记={b'LPDIRECT3D9 g_pD3D' in content}")
    if content[:20] == b"import AnyThingDraw." and b"LPDIRECT3D9 g_pD3D" in content:
        out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IdtSetting_recovered.cpp")
        with open(out, "wb") as f:
            f.write(content)
        print(f"恢复 {len(content)} 字节 -> {out}")
        break

raw.close()
