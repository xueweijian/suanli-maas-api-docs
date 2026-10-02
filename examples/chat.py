"""对话. 用法: SUANLI_API_KEY=xxx python3 chat.py [model]"""
import json, os, sys, urllib.request
BASE = "https://api.suanli.cn/v1"
KEY = os.environ["SUANLI_API_KEY"]
MODEL = sys.argv[1] if len(sys.argv) > 1 else "deepseek/deepseek-v4-flash-0731-free"
body = {"model": MODEL, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 32}
req = urllib.request.Request(BASE + "/chat/completions", data=json.dumps(body).encode(),
    method="POST", headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
with urllib.request.urlopen(req, timeout=90) as r:
    d = json.loads(r.read())
if "error" in d:
    print("REJECTED:", d["error"].get("message"))
elif "choices" in d:
    print("OK:", repr(d["choices"][0]["message"].get("content")))
else:
    print("UNKNOWN:", str(d)[:300])
