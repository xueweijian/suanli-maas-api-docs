"""模型清单. 用法: SUANLI_API_KEY=xxx python3 models_list.py"""
import json, os, urllib.request
BASE = "https://api.suanli.cn/v1"
KEY = os.environ["SUANLI_API_KEY"]
req = urllib.request.Request(BASE + "/models",
    headers={"Authorization": "Bearer " + KEY})
with urllib.request.urlopen(req, timeout=30) as r:
    d = json.loads(r.read())
print(f"count={len(d['data'])} object={d.get('object')} success={d.get('success')}")
for m in d["data"]:
    print(f" - {m['id']} | {m.get('supported_endpoint_types')}")
