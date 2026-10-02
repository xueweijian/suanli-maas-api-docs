#!/usr/bin/env python3
"""mineru 端点爆破:发散试 chat 变体(messages/image_url) + OpenAI 兼容冷门端点.
只读环境变量.输出只含状态码+摘要."""
import json, os, time, base64, urllib.request, urllib.error

BASE = "https://api.suanli.cn/v1"
KEY = os.getenv("SUANLI_API_KEY", "")
MID = "mineru/mineru2.5-pro-2604-1.2b"
H = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}

# 1x1 白点 png base64(data url)
PNG = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGA"
       "hKmMIQAAAABJRU5ErkJggg==")

def post(path, body, timeout=90):
    req = urllib.request.Request(BASE + path, data=json.dumps(body).encode(),
                                 method="POST", headers=H)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()[:700].decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try: return e.code, e.read()[:700].decode("utf-8", "replace")
        except Exception: return e.code, "unparsed"
    except Exception as e:
        return "ERR", str(e)[:150]

def get(path, timeout=30):
    req = urllib.request.Request(BASE + path, headers={"Authorization": "Bearer " + KEY})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()[:700].decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try: return e.code, e.read()[:700].decode("utf-8", "replace")
        except Exception: return e.code, "unparsed"
    except Exception as e:
        return "ERR", str(e)[:150]

tests = []
# A. chat 变体: system+user / 长文本(触发解析?) / image_url(喂图)
tests.append(("chat system+user",
    post("/chat/completions", {"model": MID, "messages": [
        {"role": "system", "content": "You are a document parser. Parse the document into markdown."},
        {"role": "user", "content": "# Hello\n\nThis is a test paragraph with a table:\n\n| a | b |\n|---|---|\n| 1 | 2 |"}],
        "max_tokens": 512})))
time.sleep(2)
tests.append(("chat image_url",
    post("/chat/completions", {"model": MID, "messages": [{
        "role": "user", "content": [
            {"type": "text", "text": "Parse this image into markdown."},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + PNG}}]}],
        "max_tokens": 512})))
time.sleep(2)
# B. OpenAI 冷门兼容端点
tests.append(("completions(legacy)",
    post("/completions", {"model": MID, "prompt": "Hello", "max_tokens": 16})))
time.sleep(2)
tests.append(("responses",
    post("/responses", {"model": MID, "input": "hi"})))
time.sleep(2)
# C. 猜 mineru/vlm 风格路径
for p in ["/parse", "/v1/parse", "/file_parse", "/ocr", "/document_parse",
          "/mineru/parse", "/parser/parse"]:
    tests.append((f"POST {p}", post(p, {"model": MID}, timeout=30)))
    time.sleep(1)
for p in ["/models/mineru/mineru2.5-pro-2604-1.2b", "/mineru"]:
    tests.append((f"GET {p}", get(p)))
    time.sleep(1)

for name, (c, r) in tests:
    print(f"[{c}] {name}")
    print("    ", r[:320].replace("\n", " "))
