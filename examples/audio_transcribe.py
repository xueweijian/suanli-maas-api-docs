"""ASR转写. 用法: SUANLI_API_KEY=xxx python3 audio_transcribe.py [wav文件]
不给文件则现场合成2秒测试音(无语音,仅验证链路)."""
import io, json, os, sys, math, struct, wave, urllib.request, urllib.error
BASE = "https://api.suanli.cn/v1"
KEY = os.environ["SUANLI_API_KEY"]
MODEL = "qwen/qwen3-asr-1.7b"

if len(sys.argv) > 1:
    wav_bytes = open(sys.argv[1], "rb").read()
    print(f"input file: {sys.argv[1]} ({len(wav_bytes)} bytes)")
else:
    buf = io.BytesIO()
    w = wave.open(buf, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(b"".join(struct.pack("<h", int(10000 * math.sin(2 * math.pi * 440 * t / 16000)))
                            for t in range(32000)))
    w.close(); wav_bytes = buf.getvalue()
    print(f"synth 2s tone ({len(wav_bytes)} bytes, no speech -> text will be empty)")

boundary = "----suanliform1234"
pre = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\n{MODEL}\r\n"
       f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; "
       f"filename=\"audio.wav\"\r\nContent-Type: audio/wav\r\n\r\n").encode() \
    + wav_bytes + f"\r\n--{boundary}--\r\n".encode()
req = urllib.request.Request(BASE + "/audio/transcriptions", data=pre, method="POST",
    headers={"Authorization": "Bearer " + KEY,
             "Content-Type": f"multipart/form-data; boundary={boundary}"})
try:
    with urllib.request.urlopen(req, timeout=120) as r:
        print(f"OK http={r.status}:", r.read()[:400].decode("utf-8", "replace"))
except urllib.error.HTTPError as e:
    print(f"FAIL http={e.code}:", e.read()[:400].decode("utf-8", "replace"))
