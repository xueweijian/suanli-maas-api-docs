"""生图. 用法: SUANLI_API_KEY=xxx python3 images.py [model] [prompt] （约60-120s）"""
import json, os, sys, base64, urllib.request
BASE = "https://api.suanli.cn/v1"
KEY = os.environ["SUANLI_API_KEY"]
MODEL = sys.argv[1] if len(sys.argv) > 1 else "black-forest-labs/flux.1-krea-dev"
PROMPT = sys.argv[2] if len(sys.argv) > 2 else \
    "a small orange cat sitting on a wooden table, photorealistic"
body = {"model": MODEL, "prompt": PROMPT}
req = urllib.request.Request(BASE + "/images/generations", data=json.dumps(body).encode(),
    method="POST", headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
print("generating... (timeout 180s)")
with urllib.request.urlopen(req, timeout=180) as r:
    d = json.loads(r.read())
url = d["data"][0]["url"]
png = base64.b64decode(url.split("file://", 1)[1])
open("cat.png", "wb").write(png)
print(f"OK saved cat.png ({len(png)} bytes)")
