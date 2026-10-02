#!/usr/bin/env python3
"""终极验证:合成一张带中英文+表格的文档图,走 mineru chat + image_url,
看回包是否含图中真实文字,判定 MaaS 版 mineru 是否真能解析文档图像."""
import json, os, time, base64, io, urllib.request, urllib.error
from PIL import Image, ImageDraw

BASE = "https://api.suanli.cn/v1"
KEY = os.getenv("SUANLI_API_KEY", "")
MID = "mineru/mineru2.5-pro-2604-1.2b"
H = {"Authorization": "Bearer " + KEY, "Content-Type": "application/json"}

# --- 合成文档图(白底黑字,1036x1036,vl-utils版面输入尺寸) ---
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
open("/tmp/mineru_doctest.png", "wb").write(buf.getvalue())
print("doc png bytes:", len(buf.getvalue()))

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

# A. Text Recognition + 真图
c, r = chat({"model": MID, "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": [
        {"type": "text", "text": "\nText Recognition:"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}}]}],
    "max_tokens": 512, "temperature": 0.0})
content = r.get("choices", [{}])[0].get("message", {}).get("content", "")
print("[A TextRec+img]", c, repr(content)[:800])
hits = [w for w in ["MinerU", "revenue", "Product", "100", "200", "Formula"] if w in content]
print("   命中词:", hits, f"{len(hits)}/6")
time.sleep(2)

# B. Layout Detection + 真图
c2, r2 = chat({"model": MID, "messages": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": [
        {"type": "text", "text": "\nLayout Detection:"},
        {"type": "image_url", "image_url": {"url": "data:image/png;base64," + b64}}]}],
    "max_tokens": 1024, "temperature": 0.0})
content2 = r2.get("choices", [{}])[0].get("message", {}).get("content", "")
print("[B Layout+img]", c2, repr(content2)[:800])
print("   含box标记:", ("box_start" in content2 or "box" in content2.lower()))
print("DONE")
