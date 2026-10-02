"""向量. 用法: SUANLI_API_KEY=xxx python3 embeddings.py [model]"""
import json, os, sys, urllib.request
BASE = "https://api.suanli.cn/v1"
KEY = os.environ["SUANLI_API_KEY"]
MODEL = sys.argv[1] if len(sys.argv) > 1 else "qwen/qwen3-embedding-8b"
body = {"model": MODEL, "input": "hello"}
req = urllib.request.Request(BASE + "/embeddings", data=json.dumps(body).encode(),
    method="POST", headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=60) as r:
    d = json.loads(r.read())
vec = d["data"][0]["embedding"]
print(f"OK dim={len(vec)} first3={[round(x, 5) for x in vec[:3]]}")
print("usage:", d.get("usage"))
