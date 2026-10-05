import ctypes, msvcrt, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DEV = "\\\\" + ".\\" + "D:"
DDB = "同类软件悬浮窗拦截助手(DesktopDrawpadBlocker)是依据 GPLv3 许可协议发布的开源软件".encode("utf-8")
IMPORT = b"import AnyThingDraw.Thread.Status;"
TARGET = 401408

raw = open(DEV, "rb", buffering=0)
h = msvcrt.get_osfhandle(raw.fileno())
k = ctypes.windll.kernel32
AL = 512
WIN = 1024 * 1024

hits = [36980964304, 68990129853, 83448458525]

for hit in hits:
    base = (max(0, hit - 500 * 1024) // AL) * AL
    buf = ctypes.create_string_buffer(WIN + AL)
    got = ctypes.c_ulonglong()
    k.SetFilePointer(h, ctypes.c_long(base & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(base >> 32)), 0)
    k.ReadFile(h, buf, len(buf), ctypes.byref(got), None)
    d = buf.raw[:got.value]
    im = d.find(IMPORT)
    if im >= 0:
        abs_imp = base + im
        file_start = abs_imp
        print(f"FOUND import at {abs_imp}")
        ra2 = (file_start // AL) * AL
        k.SetFilePointer(h, ctypes.c_long(ra2 & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(ra2 >> 32)), 0)
        cb = ctypes.create_string_buffer(TARGET + 2 * AL)
        got2 = ctypes.c_ulonglong()
        k.ReadFile(h, cb, len(cb), ctypes.byref(got2), None)
        content = cb.raw[:got2.value][file_start - ra2:file_start - ra2 + TARGET]
        if content.startswith(IMPORT):
            out = "IdtSetting_recovered.cpp"
            with open(out, "wb") as f:
                f.write(content)
            print(f"恢复 {len(content)} 字节 -> {out}")
            break

raw.close()
