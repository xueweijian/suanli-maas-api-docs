#!/usr/bin/env python3
"""mineru vl-utils同构验证:图在前+文在后(默认text_before_image=False),
采样参数全套(Default)/TextRec,看是否复刻官方两步流程."""
import json, os, time, base64, io, urllib.request, urllib.error
from PIL import Image, ImageDraw

BASE = "https://api.suanli.cn/v1"
KEY = os.getenv("SUANLI_API_KEY", "")
MID = "mineru/mineru2.5-pro-2604-1.2b"
H = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}

W = Hh = 1036
img = Image.new("RGB", (W, Hh), "white")
d = ImageDraw.Draw(img)
y = 60
d.text((60, y), "MinerU Parse Test 2026", fill="black"); y += 60
d.text((60, y), "Quarterly revenue 120 wan, growth 15 percent.", fill="black"); y += 60
d.text((60, y), "Product A sold 100 units. Product B sold 200 units.", fill="black"); y += 80
d.text((60, y), "Table: Product | Sales", fill="black"); y += 50
d.text((60, y), "Row1: A | 100", fill="black"); y += 50
d.text((60, y), "Row2: B | 200", fill="black"); y += 50
d.rectangle([60, y, 976, y + 3], fill="black"); y += 40
d.text((60, y), "Formula E = mc2 shown here.", fill="black")
buf = io.BytesIO(); img.save(buf, format="PNG")
b64 = base64.b64encode(buf.getvalue()).decode()
open("/tmp/mineru_doctest2.png", "wb").write(buf.getvalue())
URL = "data:image/png;base64," + b64

def chat(body, timeout=120):
    req = urllib.request.Request(BASE + "/chat/completions",
                                 data=json.dumps(body).encode(), method="POST", headers=H)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try: return e.code, json.loads(e.read())
        except Exception: return e.code, {}
    except Exception as e:
        return "ERR", {"_e": str(e)[:150]}

def show(tag, c, r):
    content = r.get("choices", [{}])[0].get("message", {}).get("content", "")
    print(f"[{tag}]", c, repr(content)[:700])
    hits = [w for w in ["MinerU", "revenue", "Product", "100", "200", "Formula"] if w in content]
    print("   命中:", hits, f"{len(hits)}/6")
    return content

# A. 图在前+文在后(vl-utils默认顺序) + Layout prompt + 全套采样
c, r = chat({"model": MID, "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": URL}},
        {"type": "text", "text": "\nLayout Detection:"}]}],
    "max_tokens": 1024, "temperature": 0.0, "top_p": 0.01, "top_k": 1,
    "presence_penalty": 0.0, "frequency_penalty": 0.0,
    "repetition_penalty": 1.0, "skip_special_tokens": False})
show("A layout 图前文后+全参", c, r)
time.sleep(2)
# B. 同上,Text Recognition
c, r = chat({"model": MID, "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": [
        {"type": "image_url", "image_url": {"url": URL}},
        {"type": "text", "text": "\nText Recognition:"}]}],
    "max_tokens": 512, "temperature": 0.0,
    "presence_penalty": 1.0, "frequency_penalty": 0.05,
    "repetition_penalty": 1.0, "skip_special_tokens": False})
show("B textrec 图前文后+全参", c, r)
print("DONE")
