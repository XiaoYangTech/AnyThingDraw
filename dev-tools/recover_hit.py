import ctypes, msvcrt, sys, os

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NEEDLE = "同类软件悬浮窗拦截助手(DesktopDrawpadBlocker)是依据 GPLv3 许可协议发布的开源软件".encode("utf-8")
ERASER = "双击或右键橡皮快速清空并切回批注".encode("utf-8")
IMPORT = b"import AnyThingDraw.Thread.Status;"
TARGET = 401408

hits = [36980964304, 68990129853, 83448458525]

raw = open(r"\\.\D:", "rb", buffering=0)
h = msvcrt.get_osfhandle(raw.fileno())
k = ctypes.windll.kernel32
AL = 512
WIN = 2 * 1024 * 1024  # 每个命中读 2MB 窗口

for hit in hits:
    base = (max(0, hit - 350 * 1024) // AL) * AL
    buf = ctypes.create_string_buffer(WIN + AL)
    got = ctypes.c_ulonglong()
    k.SetFilePointer(h, ctypes.c_long(base & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(base >> 32)), 0)
    k.ReadFile(h, buf, len(buf), ctypes.byref(got), None)
    d = buf.raw[:got.value]
    er = d.find(ERASER)
    im = d.find(IMPORT)
    print(f"hit@{hit}: base={base} eraser={'@'+str(base+er) if er>=0 else '无'} import={'@'+str(base+im) if im>=0 else '无'}")
    if er >= 0 and im >= 0 and 0 < im < er < 401408 * 2:
        file_start = base + im
        file_end_candidate = base + er
        length = file_end_candidate - file_start + 4096
        print(f"  文件起始={file_start}, 长度候选≈{length}")
        # 读取完整文件
        ra2 = (file_start // AL) * AL
        k.SetFilePointer(h, ctypes.c_long(ra2 & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(ra2 >> 32)), 0)
        content_buf = ctypes.create_string_buffer(TARGET + 2 * AL)
        got2 = ctypes.c_ulonglong()
        k.ReadFile(h, content_buf, len(content_buf), ctypes.byref(got2), None)
        full = content_buf.raw[:got2.value]
        off = file_start - ra2
        content = full[off:off + TARGET]
        # 验证
        ok_head = content.startswith(IMPORT)
        ok_tail = b"LPDIRECT3D9 g_pD3D" in content[-4096:]
        ok_line = content.count(b"\n") == 8119
        print(f"  头={ok_head} 尾标记={ok_tail} 行数={content.count(chr(10).encode())}")
        if ok_head and (ok_tail or ok_line):
            out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IdtSetting_recovered.cpp")
            with open(out, "wb") as f:
                f.write(content)
            print(f"已恢复 {len(content)} 字节 -> {out}")
            break

raw.close()
