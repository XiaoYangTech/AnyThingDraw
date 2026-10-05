import ctypes, msvcrt, sys, os

raw = open(r"\\.\D:", "rb", buffering=0)
h = msvcrt.get_osfhandle(raw.fileno())
k = ctypes.windll.kernel32
AL = 512
base = (36012297 // AL) * AL
k.SetFilePointer(h, ctypes.c_long(base & 0xFFFFFFFF), ctypes.byref(ctypes.c_long(base >> 32)), 0)
buf = ctypes.create_string_buffer(8192)
got = ctypes.c_ulonglong()
k.ReadFile(h, buf, 8192, ctypes.byref(got), None)
data = buf.raw[:got.value]
mk = "双击或右键橡皮快速清空并切回批注".encode("utf-8")
m = data.find(mk)
print("标记在窗口偏移:", m)
start = max(0, m - 400)
seg = data[start:m + 400]
out = seg.decode("utf-8", errors="replace")
sys_out = open(os.path.join(os.path.dirname(__file__) if "__file__" in dir() else ".", "dump_ctx.txt"), "wb")
sys_out.write(out.encode("utf-8"))
sys_out.close()
raw.close()
print("已写入 dump_ctx.txt", len(out))
